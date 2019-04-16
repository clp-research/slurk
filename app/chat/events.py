from calendar import timegm
from datetime import datetime

from flask_socketio import emit
from flask_login import login_required, current_user

from .. import socketio
from ..models.user import User
from ..models.room import Room


@socketio.on('text')
@login_required
def message_text(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.message_text:
        return False, "insufficient rights"
    if 'msg' not in payload:
        return False, 'missing argument: "msg"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.message_broadcast:
        return False, "insufficient rights"

    if 'receiver_id' in payload:
        receiver = User.query.get(payload['receiver_id']).session_id
        private = True
    elif 'room' in payload:
        room = Room.query.get(payload['room'])
        if room.read_only:
            return False, 'Room "%s" is read-only' % room.label
        receiver = room.name
        private = False
    else:
        return False, "`text` requires `room` or `receiver_id` as parameters"

    emit('message', {
        'msg': payload['msg'],
        'sender': {
            'id': current_user_id,
            'name': current_user.name,
        },
        'private_message': private,
        'timestamp': timegm(datetime.now().utctimetuple()),
    }, room=receiver, broadcast=broadcast)
    for room in current_user.rooms:
        emit('stop_typing', {'sender': current_user_id}, room=room.name)
    return True


@socketio.on('image')
@login_required
def message_image(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.message_image:
        return False, "insufficient rights"
    if 'url' not in payload:
        return False, 'missing argument: "url"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.message_broadcast:
        return False, "insufficient rights"

    if 'receiver_id' in payload:
        receiver = User.query.get(payload['receiver_id']).session_id
        private = True
    elif 'room' in payload:
        room = Room.query.get(payload['room'])
        if room.read_only:
            return False, 'Room "%s" is read-only' % room.label
        receiver = room.name
        private = False
    else:
        return False, "`image` requires `room` or `receiver_id` as parameters"

    emit('message', {
        'url': payload['url'],
        'sender': {
            'id': current_user_id,
            'name': current_user.name,
        },
        'width': payload['width'] if 'width' in payload else None,
        'height': payload['width'] if 'width' in payload else None,
        'private_message': private,
        'timestamp': timegm(datetime.now().utctimetuple()),
    }, room=receiver, broadcast=broadcast)
    for room in current_user.rooms:
        emit('stop_typing', {'sender': current_user_id}, room=room.name)
    return True
