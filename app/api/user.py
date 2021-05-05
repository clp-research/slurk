from flask_login import current_user
from flask_socketio import join_room, leave_room

from .. import socketio, db

from ..models.room import Room
from ..models.user import User
from ..api.log import log_event


@socketio.on('join_room')
def _join_room(data):
    id = data.get('user')
    room = data.get('room')

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
            'room': room.name,
            'user': user.id,
        }, room=user.session_id)
        log_event("join", user, room)
    db.session.commit()

    join_room(room.name, user.session_id)

    return True


@socketio.on('leave_room')
def _leave_room(data):
    id = data.get('user')
    room = data.get('room')

    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.user_room_leave:
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
    if room in user.current_rooms:
        user.current_rooms.remove(room)
    socketio.emit('left_room', room.name, room=user.session_id)
    log_event("leave", user, room)
    db.session.commit()
    leave_room(room.name, user.session_id)

    return True
