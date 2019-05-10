from flask_login import current_user
from flask_socketio import close_room
from sqlalchemy.exc import IntegrityError

from .. import socketio, db

from ..models.layout import Layout
from ..models.room import Room
from ..api.log import log_event


@socketio.on('get_room')
def _get_room(name):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.room_query:
        return False, "insufficient rights"
    room = Room.query.get(name)
    if room:
        return True, room.as_dict()
    else:
        return False, "room does not exist"


@socketio.on('get_room_logs')
def _get_room_logs(name):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.room_log_query:
        return False, "insufficient rights"

    room = Room.query.get(name)
    if room:
        return True, [log.as_dict() for log in room.logs]
    else:
        return False, "room does not exist"


@socketio.on('create_room')
def _create_room(name, label, data):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.room_create:
        return False, "insufficient rights"

    if 'layout' in data:
        layout = Layout.query.get(data['layout'])
        if not layout:
            return False, "layout does not exist"
    else:
        layout = None

    room = Room(
        name=name,
        label=label,
        layout=layout,
        read_only=data['read_only'] if 'read_only' in data else None,
        show_users=data['show_users'] if 'show_users' in data else None,
        show_latency=data['show_latency'] if 'show_latency' in data else None,
        static=data['static'] if 'static' in data else None,
    )
    db.session.add(room)
    try:
        db.session.commit()
        return True, room.as_dict()
    except IntegrityError as e:
        return False, str(e)


@socketio.on('close_room')
def _close_room(room):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.room_close:
        return False, "insufficient rights"

    room = Room.query.get(room)
    if not room:
        return False, "room does not exist"

    try:
        for user in room.current_users:
            if user.session_id:
                socketio.emit('left_room', room.name, room=user.session_id)
                log_event("leave", user, room)
        close_room(room.name)
        deleted = Room.query.filter_by(name=room.name).delete()
        db.session.commit()
        return True, bool(deleted)
    except IntegrityError as e:
        return False, str(e)
