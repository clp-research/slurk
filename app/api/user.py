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
    if not user:
        return False, "user does not exist"

    room = Room.query.get(room)
    if not room:
        return False, "room does not exist"

    if room not in user.rooms:
        user.rooms.append(room)
    if room not in user.current_rooms:
        user.current_rooms.append(room)
        socketio.emit('joined_room', room.as_dict(), room=user.session_id)
        print(user.name, "joined", room.name)
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
    if not user:
        return False, "user does not exist"

    room = Room.query.get(room)
    if not room:
        return False, "room does not exist"

    user.rooms.remove(room)
    if user.current_rooms.remove(room) > 0:
        socketio.emit('left_room', room.name, room=user.session_id)
        print(user.name, "left", room.name)
    db.session.commit()

    leave_room(room, user.session_id)

    return True
