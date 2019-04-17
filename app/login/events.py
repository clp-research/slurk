from calendar import timegm
from datetime import datetime

from flask import request
from flask_socketio import join_room, leave_room
from flask_login import login_required, current_user, logout_user, login_user

from .. import db, socketio


@socketio.on('connect')
@login_required
def connect():
    print(current_user.name, "connected")
    current_user.session_id = request.sid
    db.session.commit()
    if current_user.rooms.count() == 0:
        current_user.rooms.append(current_user.token.room)
    for room in current_user.rooms:
        join_room(room.name)
        if current_user not in room.current_users:
            current_user.current_rooms.append(current_user.token.room)
        socketio.emit('joined_room', {
            'room': room.as_dict(),
            'layout': room.layout.as_dict() if room.layout else None,
        }, room=current_user.session_id)
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
    db.session.commit()


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
        socketio.emit('left_room', room.name, room=current_user.session_id)
        leave_room(room.name)
        current_user.current_rooms.remove(current_user.token.room)
        print(current_user.name, "left", room.label)
    db.session.commit()
    print(current_user.name, "disconnected")
    logout_user()
