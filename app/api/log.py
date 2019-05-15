import bson
from logging import getLogger

from flask_login import current_user

from .. import socketio


def _log_event_internal(event, user, room, data):
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

    db.session.add(Log(event=event, user=user, room=room, data=bson.dumps(data)))
    db.session.commit()


def log_event(event, user, room=None, data=None):
    from .. import Event

    event_type = Event.query.get(event)
    if not event_type:
        getLogger("slurk").error('Invalid event type: %s', event)

    _log_event_internal(event_type, user, room, data)


@socketio.on("log_event")
def _log_event(data):
    from .. import Event

    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.log_event:
        return False, "insufficient rights"
    if 'event' not in data:
        return False, 'missing argument "event"'

    event = Event.query.get(data['event'])
    if not event:
        return False, f"invalid event \"{data['event']}\""

    log_event(event, current_user, data.get('room'), data.get('data'))
    return True
