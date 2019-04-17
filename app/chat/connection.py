from calendar import timegm
from datetime import datetime

from flask import request
from flask_socketio import emit
from flask_login import current_user
from sqlalchemy import event
from sqlalchemy.engine import Engine

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


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
