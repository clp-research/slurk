import bson
from logging import getLogger

from flask_login import current_user

from .. import socketio


def log_event(event, user, room=None, data=None):
    from .. import db, Log, Event

    if data is None:
        data = {}

    event_type = Event.query.get(event)
    if not event_type:
        getLogger("slurk").error('Invalid event type: %s', event)

    if event == "join":
        getLogger("slurk").info('%s joined %s', user.name, room.label)
    if event == "leave":
        getLogger("slurk").info('%s left %s', user.name, room.label)
    if event == "connect":
        getLogger("slurk").info('%s connected', user.name)
    if event == "disconnect":
        getLogger("slurk").info('%s disconnected', user.name)

    db.session.add(Log(event=event_type, user=user, room=room, data=bson.dumps(data)))
    db.session.commit()
