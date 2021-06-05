from flask import request, current_app
from flask_login import login_required, logout_user, current_user

from app.extensions.events import socketio
from app.models import Log


@socketio.on('connect')
@login_required
def connect():
    current_app.logger.error(f"LOADING USER FROM REQUEST: {[r.id for r in current_user.rooms]}")
    current_user.session_id = request.sid
    current_app.session.commit()
    for room in current_user.rooms:
        current_user.join_room(room)
    Log.add("connect", current_user)


@socketio.on('disconnect')
@login_required
def disconnect():
    for room in current_user.rooms:
        current_user.leave_room(room)
    current_user.session_id = None
    current_app.session.commit()
    Log.add("disconnect", current_user)
    logout_user()
