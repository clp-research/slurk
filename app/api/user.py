from logging import getLogger

from flask_login import current_user
from flask_socketio import join_room, leave_room

from .. import socketio, db

from ..models.room import Room
from ..models.user import User


@socketio.on('get_user')
def _get_user(id):
    current_id = current_user.get_id()
    if not current_id:
        return False, "invalid session id"

    if id and not current_user.token.permissions.user_query:
        return False, "insufficient rights"
    user = User.query.get(id or current_id)
    if user:
        return True, user.as_dict()
    else:
        return False, "user does not exist"


@socketio.on('get_user_task')
def _get_user_task(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.task_query:
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, user.token.task.as_dict() if user.token and user.token.task else None
    else:
        return False, "user does not exist"


@socketio.on('get_user_token')
def _get_user_task(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.token_query:
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, user.token.as_dict() if user.token else None
    else:
        return False, "user does not exist"


@socketio.on('get_user_permissions')
def _get_user_permissions(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.permissions_query:
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, user.token.permissions.as_dict()
    else:
        return False, "user does not exist"


@socketio.on('get_user_rooms')
def _get_user_rooms(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.user_room_query:
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, [room.as_dict() for room in user.rooms]
    else:
        return False, "user does not exist"


@socketio.on('join_room')
def _join_room(id, room):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.user_room_join:
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user
    if not user or not user.session_id:
        return False, "user does not exist"

    room = Room.query.get(room)
    if not room:
        return False, "room does not exist"

    if room not in user.rooms:
        user.rooms.append(room)
    if room not in user.current_rooms:
        user.current_rooms.append(room)
        socketio.emit('joined_room', {
            'room': room.as_dict(),
            'layout': room.layout.as_dict() if room.layout else None,
        }, room=user.session_id)
        getLogger("slurk").info('%s joined %s', user.name, room.name)
    db.session.commit()

    join_room(room, user.session_id)

    return True


@socketio.on('leave_room')
def _leave_room(id, room):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.user_room_join:
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user
    if not user or not user.session_id:
        return False, "user does not exist"

    room = Room.query.get(room)
    if not room:
        return False, "room does not exist"

    user.rooms.remove(room)
    if user.current_rooms.remove(room) > 0:
        socketio.emit('left_room', room.name, room=user.session_id)
        getLogger("slurk").info('%s left %s', user.name, room.name)
    db.session.commit()
    leave_room(room, user.session_id)

    return True
