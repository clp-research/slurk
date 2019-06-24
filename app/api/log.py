import bson
from logging import getLogger


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
