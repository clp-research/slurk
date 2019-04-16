from flask_login import current_user

from .. import db, socketio

from . import Base


class Permissions(Base):
    __tablename__ = 'Permissions'

    query_user = db.Column(db.Boolean, nullable=False, default=False)
    query_room = db.Column(db.Boolean, nullable=False, default=False)
    query_permissions = db.Column(db.Boolean, nullable=False, default=False)
    query_layout = db.Column(db.Boolean, nullable=False, default=False)
    message_text = db.Column(db.Boolean, nullable=False, default=False)
    message_image = db.Column(db.Boolean, nullable=False, default=False)
    message_command = db.Column(db.Boolean, nullable=False, default=False)
    message_history = db.Column(db.Boolean, nullable=False, default=False)
    message_broadcast = db.Column(db.Boolean, nullable=False, default=False)
    token_generate = db.Column(db.Boolean, nullable=False, default=False)
    token_invalidate = db.Column(db.Boolean, nullable=False, default=False)
    token = db.relationship("Token", backref="permissions", uselist=False)

    def as_dict(self):
        return dict({
            'query': {
                'user': self.query_user,
                'room': self.query_room,
                'permissions': self.query_permissions,
                'layout': self.query_layout,
            },
            'message': {
                'text': self.message_text,
                'image': self.message_image,
                'command': self.message_command,
                'history': self.message_history,
                'broadcast': self.message_broadcast,
            },
            'token': {
                'generate': self.token_generate,
                'invalidate': self.token_invalidate,
            },
        }, **super(Permissions, self).as_dict())


@socketio.on('get_permissions')
def _get_permissions(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.query_permissions:
        return False, "insufficient rights"
    permissions = Permissions.query.get(id)
    if permissions:
        return True, permissions.as_dict()
    else:
        return False, "permissions does not exist"
