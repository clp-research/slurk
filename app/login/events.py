from calendar import timegm
from datetime import datetime

from flask import request
from flask_socketio import join_room, leave_room
from flask_login import login_required, current_user, logout_user

from .. import db, socketio


@socketio.on('connect')
@login_required
def connect():
    print(current_user.name, "connected")
    current_user.session_id = request.sid
    db.session.commit()
    for room in current_user.rooms:
        join_room(room.name)
        socketio.emit('status', {
            'type': 'join',
            'user': current_user.id,
            'room': room.name,
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=room.name)
        print(current_user.name, "joined", room.label)


@socketio.on('disconnect')
@login_required
def disconnect():
    for room in current_user.rooms:
        socketio.emit('status', {
            'type': 'leave',
            'user': current_user.id,
            'room': room.name,
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=room.name)
        leave_room(room.name)
        print(current_user.name, "left", room.label)
    print(current_user.name, "disconnected")
    logout_user()
