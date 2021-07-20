from datetime import datetime

from flask.globals import current_app
from flask_login import login_required, current_user

from slurk.extensions.events import socketio
from slurk.models import User, Room, Log


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
            "user_message", {"user": user, "message": payload["msg"]}, room=str(room.id)
        )


@socketio.event
@login_required
def text(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.send_message:
        return False, "insufficient rights"
    if "msg" not in payload:
        return False, 'missing argument: "msg"'
    if "room" not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get("broadcast", False)
    if broadcast and not current_user.token.permissions.broadcast:
        return False, "insufficient rights"

    db = current_app.session
    room = db.query(Room).get(payload["room"])
    if not room:
        return False, "Room not found"
    if current_user not in room.users:
        return False, "Not in room"

    if room.layout.read_only:
        return False, 'Room "%s" is read-only' % room.label

    if "receiver_id" in payload:
        if not current_user.token.permissions.private_message:
            return False, "You are not allowed to send private text messages"
        receiver_id = payload["receiver_id"]
        receiver = db.query(User).get(receiver_id)
        if not receiver or not receiver.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        private = True
    else:
        receiver = None
        private = False

    user = {
        "id": current_user_id,
        "name": current_user.name,
    }

    socketio.emit(
        "text_message",
        {
            "msg": payload["msg"],
            "user": user,
            "room": str(room.id) if room else None,
            "timestamp": str(datetime.utcnow()),
            "private": private,
            "html": payload.get("html", False),
        },
        room=receiver.session_id if private else str(room.id),
        broadcast=broadcast,
    )
    Log.add(
        "text_message",
        current_user,
        room,
        receiver,
        data={
            "message": payload["msg"],
            "html": payload.get("html", False),
        },
    )
    for room in current_user.rooms:
        socketio.emit("stop_typing", {"user": user}, room=str(room.id))
    return True


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
    if "room" not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get("broadcast", False)
    if broadcast and not current_user.token.permissions.broadcast:
        return False, "insufficient rights"

    db = current_app.session
    room = db.query(Room).get(payload["room"])
    if not room:
        return False, "Room not found"

    if "receiver_id" in payload:
        receiver_id = payload["receiver_id"]
        receiver = db.query(User).get(receiver_id)
        if not receiver or not receiver.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        private = True
    else:
        receiver = None
        private = False

    user = {
        "id": current_user_id,
        "name": current_user.name,
    }
    socketio.emit(
        "command",
        {
            "command": payload["command"],
            "user": user,
            "room": str(room.id) if room else None,
            "timestamp": str(datetime.utcnow()),
            "private": private,
        },
        room=receiver.session_id if private else str(room.id),
        broadcast=broadcast,
    )
    Log.add(
        "command",
        current_user,
        room,
        receiver,
        data={
            "command": payload["command"],
        },
    )
    for room in current_user.rooms:
        socketio.emit("stop_typing", {"user": user}, room=str(room.id))
    return True


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
    if "room" not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get("broadcast", False)
    if broadcast and not current_user.token.permissions.broadcast:
        return False, "insufficient rights"

    db = current_app.session
    room = db.query(Room).get(payload["room"])
    if room.layout.read_only:
        return False, 'Room "%s" is read-only' % room.label

    if "receiver_id" in payload:
        if not current_user.token.permissions.private_message:
            return False, "You are not allowed to send private image messages"
        receiver_id = payload["receiver_id"]
        receiver = db.query(User).get(receiver_id)
        if not receiver or not receiver.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        private = True
    else:
        receiver = None
        private = False

    user = {
        "id": current_user_id,
        "name": current_user.name,
    }
    width = payload["width"] if "width" in payload else None
    height = payload["height"] if "height" in payload else None
    socketio.emit(
        "image_message",
        {
            "url": payload["url"],
            "user": user,
            "width": width,
            "height": height,
            "room": str(room.id) if room else None,
            "timestamp": str(datetime.utcnow()),
            "private": private,
        },
        room=receiver.session_id if private else str(room.id),
        broadcast=broadcast,
    )
    Log.add(
        "image_message",
        current_user,
        room,
        receiver,
        data={
            "url": payload["url"],
            "width": width,
            "height": height,
        },
    )
    for room in current_user.rooms:
        socketio.emit("stop_typing", {"user": user}, room=str(room.id))
    return True
