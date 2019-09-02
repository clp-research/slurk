from calendar import timegm
from datetime import datetime

from flask_socketio import emit
from flask_login import login_required, current_user

from .. import socketio
from ..models.user import User
from ..models.room import Room

from ..api.log import log_event


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
            'name': current_user.name,
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
    if 'room' not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.message_broadcast:
        return False, "insufficient rights"

    room = Room.query.get(payload['room'])
    if not room:
        return False, 'Room not found'

    if room.read_only:
        return False, 'Room "%s" is read-only' % room.label

    if 'receiver_id' in payload:
        if not current_user.token.permissions.message_text:
            return False, 'You are not allowed to send private text messages'
        receiver_id = payload['receiver_id']
        user = User.query.get(receiver_id)
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        receiver = user.session_id
        private = True
    else:
        receiver = room.name
        private = False

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    emit('text_message', {
        'msg': payload['msg'],
        'user': user,
        'room': room.name if room else None,
        'timestamp': timegm(datetime.now().utctimetuple()),
        'private': private,
        'html': payload.get('html', False)
    }, room=receiver, broadcast=broadcast)
    log_event("text_message", current_user, room, data={'receiver': payload['receiver_id'] if private else None,
                                                        'message': payload['msg'], 'html': payload.get('html', False)})
    for room in current_user.rooms:
        emit('stop_typing', {'user': user}, room=room.name)
    return True


@socketio.on('message_command')
@login_required
def message_command(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.message_command:
        return False, "insufficient rights"
    if 'command' not in payload:
        return False, 'missing argument: "command"'
    if 'room' not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.message_broadcast:
        return False, "insufficient rights"

    room = Room.query.get(payload['room'])
    if not room:
        return False, 'Room not found'

    if 'receiver_id' in payload:
        receiver_id = payload['receiver_id']
        user = User.query.get(receiver_id)
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        receiver = user.session_id
        private = True
    else:
        receiver = room.name
        private = False

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    emit('command', {
        'command': payload['command'],
        'user': user,
        'room': room.name if room else None,
        'timestamp': timegm(datetime.now().utctimetuple()),
        'private': private,
    }, room=receiver, broadcast=broadcast)
    log_event("command", current_user, room, data={'receiver': payload['receiver_id'] if private else None, 'command':
        payload['command']})
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
    if 'room' not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.message_broadcast:
        return False, "insufficient rights"

    room = Room.query.get(payload['room'])
    if room.read_only:
        return False, 'Room "%s" is read-only' % room.label

    if 'receiver_id' in payload:
        if not current_user.token.permissions.message_text:
            return False, 'You are not allowed to send private image messages'
        receiver_id = payload['receiver_id']
        user = User.query.get(receiver_id)
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        receiver = user.session_id
        private = True
    else:
        receiver = room.name
        private = False

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    width = payload['width'] if 'width' in payload else None
    height = payload['height'] if 'height' in payload else None
    emit('image_message', {
        'url': payload['url'],
        'user': user,
        'width': width,
        'height': height,
        'room': room.name if room else None,
        'timestamp': timegm(datetime.now().utctimetuple()),
        'private': private,
    }, room=receiver, broadcast=broadcast)
    log_event("image_message", current_user, room, data={'receiver': payload['receiver_id'] if private else None,
                                                         'url': payload['url'],
                                                         'width': width,
                                                         'height': height})
    for room in current_user.rooms:
        emit('stop_typing', {'user': user}, room=room.name)
    return True
