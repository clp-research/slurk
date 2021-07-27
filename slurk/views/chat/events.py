from datetime import datetime

from flask.globals import current_app
from flask_login import login_required, current_user

from slurk.extensions.events import socketio
from slurk.models import User, Room, Log, Task


@socketio.event
def room_created(payload):
    db = current_app.session
    room = db.query(Room).get(payload["room"]) if "room" in payload else None
    task = db.query(Task).get(payload["task"]) if "task" in payload else None

    if "room" not in payload:
        False, 'Missing argument "room"'
    if not room:
        return False, f'User "{room}" does not exist'
    if "task" in payload and task is None:
        return False, f'Task "{task}" does not exist'

    socketio.emit("new_room", {"room": room.id}, broadcast=True)

    users = []
    for user in room.users:
        users.append({"id": user.id, "name": user.name})

    socketio.emit(
        "new_task_room",
        {"room": room.id, "task": task.id, "users": users},
        broadcast=True,
    )
    return True


@socketio.event
def keypress(message):
    typing = message.get("typing", None)
    if typing is None:
        return

    current_user_id = current_user.get_id()
    if not current_user_id:
        return

    for room in current_user.rooms:
        user = {
            "id": current_user_id,
            "name": current_user.name,
        }
        if typing:
            socketio.emit("start_typing", {"user": user}, room=str(room.id))
        else:
            socketio.emit("stop_typing", {"user": user}, room=str(room.id))


@socketio.event
def typed_message(payload):
    """
    This function handles live-typing mode. It is called when 'typed_message'
    event is fired and broadcasts the current message that the user typed to
    the room through 'user_message' event.
    """
    current_user_id = current_user.get_id()
    if not current_user_id:
        return

    for room in current_user.rooms:
        user = {
            "id": current_user_id,
            "name": current_user.name,
        }
        socketio.emit(
            "user_message",
            {"user": user, "message": payload["message"]},
            room=str(room.id),
        )


def emit_message(event, payload, data):
    broadcast = data["broadcast"] = payload.get("broadcast", False)

    db = current_app.session
    room = db.query(Room).get(payload["room"]) if "room" in payload else None

    if broadcast:
        if not current_user.token.permissions.broadcast:
            return False, "You are not allowed to broadcast"

        target = None
        private = False
    else:
        if "receiver_id" in payload:
            if not current_user.token.permissions.send_privately:
                return False, "You are not allowed to send privately"
            receiver_id = payload["receiver_id"]
            receiver = db.query(User).get(receiver_id)
            if not receiver:
                return False, f'User "{receiver_id}" does not exist'
            if not receiver.session_id:
                return False, f'User "{receiver_id}" is not logged in'
            target = receiver.session_id
            private = True
        else:
            if "room" not in payload:
                return False, 'missing argument: "room"'
            if not room:
                return False, "Room not found"
            if current_user not in room.users:
                return False, "Not in room"
            if room.layout.read_only:
                return False, f"Room {room.label} is read-only"
            target = str(room.id)
            private = False

    user = dict(id=current_user.get_id(), name=current_user.name)

    socketio.emit(
        event,
        dict(
            user=user,
            room=room.id if room else None,
            timestamp=str(datetime.utcnow()),
            private=private,
            **data,
        ),
        room=target,
        broadcast=broadcast,
    )

    Log.add(
        event=event,
        user=current_user,
        room=room,
        receiver=receiver if private and not broadcast else None,
        data=data,
    )

    if room:
        for room in current_user.rooms:
            socketio.emit("stop_typing", {"user": user}, room=str(room.id))

    return True


@socketio.event
@login_required
def text(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"

    html = payload.get("html", False)
    if not current_user.token.permissions.send_html_message and (
        html or not current_user.token.permissions.send_message
    ):
        return False, "insufficient rights"
    if "message" not in payload:
        return False, 'missing argument: "message"'

    return emit_message(
        "text_message",
        payload,
        data=dict(message=payload["message"], html=html),
    )


@socketio.event
@login_required
def message_command(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.send_command:
        return False, "insufficient rights"
    if "command" not in payload:
        return False, 'missing argument: "command"'

    return emit_message("command", payload, data=dict(command=payload["command"]))


@socketio.event
@login_required
def image(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.send_image:
        return False, "insufficient rights"
    if "url" not in payload:
        return False, 'missing argument: "url"'

    return emit_message(
        "image_message",
        payload,
        data=dict(
            url=payload["url"],
            width=payload.get("width"),
            height=payload.get("height"),
        ),
    )
