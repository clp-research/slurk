from calendar import timegm
from datetime import datetime

from flask_socketio import emit
from flask_login import login_required, current_user

from .. import socketio
from ..models.user import User
from ..models.room import Room


@socketio.on('keypress')
def keypress(message):
    last_typing = message.get('last_keypress', None)
    if not last_typing:
        return

    current_user_id = current_user.get_id()
    if not current_user_id:
        return

    for room in current_user.rooms:
        user = {
            'id': current_user_id,
            'name': current_user.name
        }
        if last_typing == 0:
            emit('start_typing', {'user': user}, room=room.name)
        elif last_typing == 3:
            emit('stop_typing', {'user': user}, room=room.name)


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
        user = User.query.get(payload['receiver_id'])
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % user.name
        receiver = user.session_id
        private = True
    elif 'room' in payload:
        room = Room.query.get(payload['room'])
        if room.read_only:
            return False, 'Room "%s" is read-only' % room.label
        receiver = room.name
        private = False
    else:
        return False, "`text` requires `room` or `receiver_id` as parameters"

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    emit('message', {
        'msg': payload['msg'],
        'user': user,
        'private_message': private,
        'timestamp': timegm(datetime.now().utctimetuple()),
    }, room=receiver, broadcast=broadcast)
    for room in current_user.rooms:
        emit('stop_typing', {'user': user}, room=room.name)
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
        user = User.query.get(payload['receiver_id'])
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % user.name
        receiver = user.session_id
        private = True
    elif 'room' in payload:
        room = Room.query.get(payload['room'])
        if room.read_only:
            return False, 'Room "%s" is read-only' % room.label
        receiver = room.name
        private = False
    else:
        return False, "`image` requires `room` or `receiver_id` as parameters"

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    emit('message', {
        'url': payload['url'],
        'user': user,
        'width': payload['width'] if 'width' in payload else None,
        'height': payload['width'] if 'width' in payload else None,
        'private_message': private,
        'timestamp': timegm(datetime.now().utctimetuple()),
    }, room=receiver, broadcast=broadcast)
    for room in current_user.rooms:
        emit('stop_typing', {'user': user}, room=room.name)
    return True
