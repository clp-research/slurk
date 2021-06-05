from calendar import timegm
from datetime import datetime

from flask_socketio import emit
from flask.globals import current_app
from flask_login import login_required, current_user

from app.extensions.events import socketio
from app.models import User, Room, Log
from app.extensions.events import socketio


@socketio.on('keypress')
def keypress(message):
    is_typing = message['typing']
    current_user_id = current_user.get_id()
    if not current_user_id:
        return
    for room in current_user.rooms:
        user = {
            'id': current_user_id,
            'name': current_user.name,
        }
        if is_typing:
            emit('start_typing', {'user': user}, room=str(room.id))
        else:
            emit('stop_typing', {'user': user}, room=str(room.id))


@socketio.event
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
            socketio.emit('start_typing', {'user': user}, room=str(room.id))
        elif last_typing == 3:
            socketio.emit('stop_typing', {'user': user}, room=str(room.id))


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
            'id': current_user_id,
            'name': current_user.name,
        }
        socketio.emit('user_message', {'user': user, 'message': payload['msg']}, room=str(room.id))


@socketio.event
@login_required
def text(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.send_message:
        return False, "insufficient rights"
    if 'msg' not in payload:
        return False, 'missing argument: "msg"'
    if 'room' not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.broadcast:
        return False, "insufficient rights"

    db = current_app.session
    room = db.query(Room).get(payload['room'])
    if not room:
        return False, 'Room not found'
    if current_user not in room.users:
        return False, 'Not in room'

    if room.layout.read_only:
        return False, 'Room "%s" is read-only' % room.label

    if 'receiver_id' in payload:
        if not current_user.token.permissions.private_message:
            return False, 'You are not allowed to send private text messages'
        receiver_id = payload['receiver_id']
        user = db.query(User).get(receiver_id)
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        receiver = user.session_id
        private = True
    else:
        receiver = str(room.id)
        private = False

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    print(user)
    print(payload)
    socketio.emit('text_message', {
        'msg': payload['msg'],
        'user': user,
        'room': str(room.id) if room else None,
        'timestamp': timegm(datetime.now().utctimetuple()),
        'private': private,
        'html': payload.get('html', False)
    }, room=receiver, broadcast=broadcast)
    Log.add("text_message", current_user, room, data={'receiver': payload['receiver_id'] if private else None,
                                                      'message': payload['msg'], 'html': payload.get('html', False)})
    for room in current_user.rooms:
        socketio.emit('stop_typing', {'user': user}, room=str(room.id))
    return True


@socketio.event
@login_required
def message_command(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.send_command:
        return False, "insufficient rights"
    if 'command' not in payload:
        return False, 'missing argument: "command"'
    if 'room' not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.broadcast:
        return False, "insufficient rights"

    db = current_app.session
    room = db.query(Room).get(payload['room'])
    if not room:
        return False, 'Room not found'

    if 'receiver_id' in payload:
        receiver_id = payload['receiver_id']
        user = db.query(User).get(receiver_id)
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        receiver = user.session_id
        private = True
    else:
        receiver = str(room.id)
        private = False

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    socketio.emit('command', {
        'command': payload['command'],
        'user': user,
        'room': str(room.id) if room else None,
        'timestamp': timegm(datetime.now().utctimetuple()),
        'private': private,
    }, room=receiver, broadcast=broadcast)
    Log.add("command", current_user, room, data={'receiver': payload['receiver_id'] if private else None, 'command':
                                                 payload['command']})
    for room in current_user.rooms:
        socketio.emit('stop_typing', {'user': user}, room=str(room.id))
    return True


@socketio.event
@login_required
def image(payload):
    current_user_id = current_user.get_id()
    if not current_user_id:
        return False, "invalid session id"
    if not current_user.token.permissions.send_image:
        return False, "insufficient rights"
    if 'url' not in payload:
        return False, 'missing argument: "url"'
    if 'room' not in payload:
        return False, 'missing argument: "room"'

    broadcast = payload.get('broadcast', False)
    if broadcast and not current_user.token.permissions.broadcast:
        return False, "insufficient rights"

    db = current_app.session
    room = db.query(Room).get(payload['room'])
    if room.layout.read_only:
        return False, 'Room "%s" is read-only' % room.label

    if 'receiver_id' in payload:
        if not current_user.token.permissions.private_message:
            return False, 'You are not allowed to send private image messages'
        receiver_id = payload['receiver_id']
        user = db.query(User).get(receiver_id)
        if not user or not user.session_id:
            return False, 'User "%s" does not exist' % receiver_id
        receiver = user.session_id
        private = True
    else:
        receiver = str(room.id)
        private = False

    user = {
        'id': current_user_id,
        'name': current_user.name,
    }
    width = payload['width'] if 'width' in payload else None
    height = payload['height'] if 'height' in payload else None
    socketio.emit('image_message', {
        'url': payload['url'],
        'user': user,
        'width': width,
        'height': height,
        'room': str(room.id) if room else None,
        'timestamp': timegm(datetime.now().utctimetuple()),
        'private': private,
    }, room=receiver, broadcast=broadcast)
    Log.add("image_message", current_user, room, data={'receiver': payload['receiver_id'] if private else None,
                                                       'url': payload['url'],
                                                       'width': width,
                                                       'height': height})
    for room in current_user.rooms:
        socketio.emit('stop_typing', {'user': user}, room=str(room.id))
    return True
