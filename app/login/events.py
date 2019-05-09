from logging import getLogger

from calendar import timegm
from datetime import datetime

from flask import request
from flask_socketio import join_room, leave_room
from flask_login import login_required, current_user, logout_user, login_user

from .. import db, socketio


@socketio.on('connect')
@login_required
def connect():
    getLogger("slurk").info('%s connected', current_user.name)
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
        }, room=request.sid)
        socketio.emit('status', {
            'type': 'join',
            'user': {
                'id': current_user.id,
                'name': current_user.name,
            },
            'room': room.name,
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=room.name)
        getLogger("slurk").info('%s joined %s', current_user.name, room.label)
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
        if current_user.session_id:
            socketio.emit('left_room', room.name, room=current_user.session_id)
        leave_room(room.name)
        current_user.current_rooms.remove(current_user.token.room)
        getLogger("slurk").info('%s left %s', current_user.name, room.label)
    db.session.commit()
    getLogger("slurk").info('%s disconnected', current_user.name)
    logout_user()
