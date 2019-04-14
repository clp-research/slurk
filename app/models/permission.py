from flask import request

from .. import db, socketio

from . import Base
from .user import User


class Permissions(Base):
    __tablename__ = 'Permissions'

    query_user = db.Column(db.Boolean, nullable=False, default=False)
    query_room = db.Column(db.Boolean, nullable=False, default=False)
    query_permissions = db.Column(db.Boolean, nullable=False, default=False)
    message_send = db.Column(db.Boolean, nullable=False, default=False)
    message_history = db.Column(db.Boolean, nullable=False, default=False)
    message_broadcast = db.Column(db.Boolean, nullable=False, default=False)
    token = db.relationship("Token", backref="permissions", uselist=False)

    def __repr__(self):
        return "<Permission(query='%s', message='%s')>" % ({'user': self.query_user,
                                                            'room': self.query_room,
                                                            'permissions': self.query_permissions},
                                                           {'send': self.message_send,
                                                            'history': self.message_history,
                                                            'broadcast': self.message_broadcast})

    def as_dict(self):
        return dict({
            'query': {
                'user': self.query_user,
                'room': self.query_room,
                'permissions': self.query_permissions,
            },
            'message': {
                'send': self.message_send,
                'history': self.message_history,
                'broadcast': self.message_broadcast,
            }
        }, **super(Permissions, self).as_dict())


@socketio.on('get_permissions_by_user')
def _get_permissions_by_user(id):
    user = User.query.filter_by(session_id=request.sid).first()
    if not user:
        return False, "invalid session id"
    if id:
        if not user.token.permissions.query_permissions:
            return False, "insufficient rights"
        user = User.query.get(id)
    if user:
        return True, user.token.permissions.as_dict()
    else:
        return False, "user does not exist"


@socketio.on('get_permissions')
def _get_permissions(id):
    user = User.query.filter_by(session_id=request.sid).first()
    if not user:
        return False, "invalid session id"
    if not user.token.permissions.query_permissions:
        return False, "insufficient rights"
    permissions = Permissions.query.get(id)
    if permissions:
        return True, permissions.as_dict()
    else:
        return False, "permissions does not exist"
