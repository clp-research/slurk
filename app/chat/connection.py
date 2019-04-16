from calendar import timegm
from datetime import datetime

from flask import request
from flask_socketio import emit
from flask_login import current_user

from .. import socketio


@socketio.on('my_ping')
def ping(message):
    emit('my_pong', {'timestamp': timegm(datetime.now().utctimetuple())}, room=request.sid)

    last_typing = message['typing']
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
