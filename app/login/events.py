from calendar import timegm
from datetime import datetime

from flask import request, current_app
from flask_socketio import join_room, leave_room
from flask_login import login_required, logout_user, current_user

from .. import socketio
from ..api.log import log_event


@socketio.on('connect')
@login_required
def connect():
    current_user.session_id = request.sid
    current_app.session.commit()

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
        log_event("join", current_user, room)

    log_event("connect", current_user)


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
        log_event("leave", current_user, room)
    current_user.session_id = None
    current_app.session.commit()
    log_event("disconnect", current_user)
    logout_user()
