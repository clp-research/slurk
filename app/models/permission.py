from .. import db

from . import Base


class Permissions(Base):
    __tablename__ = 'Permissions'

    user_query = db.Column(db.Boolean, nullable=False, default=False)
    user_kick = db.Column(db.Boolean, nullable=False, default=False)
    user_permissions_query = db.Column(db.Boolean, nullable=False, default=False)
    user_permissions_update = db.Column(db.Boolean, nullable=False, default=False)
    user_room_join = db.Column(db.Boolean, nullable=False, default=False)
    user_room_leave = db.Column(db.Boolean, nullable=False, default=False)
    message_text = db.Column(db.Boolean, nullable=False, default=False)
    message_image = db.Column(db.Boolean, nullable=False, default=False)
    message_command = db.Column(db.Boolean, nullable=False, default=False)
    message_history = db.Column(db.Boolean, nullable=False, default=False)
    message_broadcast = db.Column(db.Boolean, nullable=False, default=False)
    room_query = db.Column(db.Boolean, nullable=False, default=False)
    room_create = db.Column(db.Boolean, nullable=False, default=False)
    room_close = db.Column(db.Boolean, nullable=False, default=False)
    layout_query = db.Column(db.Boolean, nullable=False, default=False)
    token_generate = db.Column(db.Boolean, nullable=False, default=False)
    token_invalidate = db.Column(db.Boolean, nullable=False, default=False)
    token_remove = db.Column(db.Boolean, nullable=False, default=False)
    token = db.relationship("Token", backref="permissions", uselist=False)

    def as_dict(self):
        return dict({
            'user': {
                'query': self.user_query,
                'kick': self.user_kick,
                'permissions': {
                    'query': self.user_permissions_query,
                    'update': self.user_permissions_update,
                },
                'room': {
                    'join': self.user_room_join,
                    'leave': self.user_room_leave,
                },
            },
            'message': {
                'text': self.message_text,
                'image': self.message_image,
                'command': self.message_command,
                'history': self.message_history,
                'broadcast': self.message_broadcast,
            },
            'room': {
                'query': self.room_query,
                'create': self.room_create,
                'close': self.room_close,
            },
            'layout': {
                'query': self.layout_query,
            },
            'token': {
                'generate': self.token_generate,
                'invalidate': self.token_invalidate,
                'remove': self.token_remove,
            },
        }, **super(Permissions, self).as_dict())
