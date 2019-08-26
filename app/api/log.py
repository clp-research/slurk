import bson
from logging import getLogger

from ..models.room import Room
from ..models.user import User

from .. import socketio

from flask_login import login_required, current_user


def log_event(event, user, room=None, data=None):
    from .. import db, Log

    if not data:
        data = {}

    if event == "join":
        getLogger("slurk").info('%s joined %s', user.name, room.label)
    if event == "leave":
        getLogger("slurk").info('%s left %s', user.name, room.label)
    if event == "connect":
        getLogger("slurk").info('%s connected', user.name)
    if event == "disconnect":
        getLogger("slurk").info('%s disconnected', user.name)

    log = Log(event=event, user=user, room=room, data=bson.dumps(data))
    db.session.add(log)
    db.session.commit()
    return log

@socketio.on('log')
@login_required
def log(data):
    
    sender = current_user if 'sender_id' not in data else User.query.get(data['sender_id'])
    if not sender:
        return False, "sender not found"

    if 'room' in data:
        room = Room.query.get(data['room'])
        if not room:
            return False, "room not found"

    reduced_data = data
    if 'type' in data: del data['type']
    if 'room' in data: del data['room']
    if 'sender_id' in data: del data['sender_id']

    log_event(data["type"], current_user, room=room, data=reduced_data)