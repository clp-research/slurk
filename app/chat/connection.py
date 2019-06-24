from flask_socketio import emit
from flask_login import current_user

from .. import socketio


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
            emit('start_typing', {'user': user}, room=room.name)
        else:
            emit('stop_typing', {'user': user}, room=room.name)
