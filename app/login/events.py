from calendar import timegm
from datetime import datetime

from flask import request
from flask_socketio import join_room, leave_room
from flask_login import login_required, current_user, logout_user, login_user

from .. import db, socketio
from ..models.user import User
from ..models.token import Token


@socketio.on('connect')
@login_required
def connect():
    print(current_user.name, "connected")
    current_user.session_id = request.sid
    db.session.commit()
    if current_user.rooms.count() == 0:
        current_user.rooms.append(current_user.token.room)
        db.session.commit()
    for room in current_user.rooms:
        join_room(room.name)
        socketio.emit('status', {
            'type': 'join',
            'user': {
                'id': current_user.id,
                'name': current_user.name,
            },
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
            'user': {
                'id': current_user.id,
                'name': current_user.name,
            },
            'room': room.name,
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=room.name)
        leave_room(room.name)
        print(current_user.name, "left", room.label)
    print(current_user.name, "disconnected")
    logout_user()
