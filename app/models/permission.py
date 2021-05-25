from sqlalchemy import Column, Boolean
from sqlalchemy.orm import relationship

from .common import Common


class Permissions(Common):
    __tablename__ = 'Permissions'

    user_query = Column(Boolean, nullable=False, default=False)
    user_log_event = Column(Boolean, nullable=False, default=False)
    user_room_join = Column(Boolean, nullable=False, default=False)
    user_room_leave = Column(Boolean, nullable=False, default=False)
    message_text = Column(Boolean, nullable=False, default=False)
    message_image = Column(Boolean, nullable=False, default=False)
    message_command = Column(Boolean, nullable=False, default=False)
    message_broadcast = Column(Boolean, nullable=False, default=False)
    room_query = Column(Boolean, nullable=False, default=False)
    room_log_query = Column(Boolean, nullable=False, default=False)
    room_create = Column(Boolean, nullable=False, default=False)
    room_update = Column(Boolean, nullable=False, default=False)
    room_delete = Column(Boolean, nullable=False, default=False)
    layout_query = Column(Boolean, nullable=False, default=False)
    layout_create = Column(Boolean, nullable=False, default=False)
    layout_update = Column(Boolean, nullable=False, default=False)
    task_create = Column(Boolean, nullable=False, default=False)
    task_update = Column(Boolean, nullable=False, default=False)
    task_query = Column(Boolean, nullable=False, default=False)
    token_generate = Column(Boolean, nullable=False, default=False)
    token_query = Column(Boolean, nullable=False, default=False)
    token_invalidate = Column(Boolean, nullable=False, default=False)
    token_update = Column(Boolean, nullable=False, default=False)
    token = relationship("Token", backref="permissions", uselist=False)

    def as_dict(self):
        return dict({
            'user': {
                'query': self.user_query,
                'log': {
                    'event': self.user_log_event,
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
                'broadcast': self.message_broadcast,
            },
            'room': {
                'query': self.room_query,
                'create': self.room_create,
                'update': self.room_update,
                'delete': self.room_delete,
                'log': {
                    'query': self.room_log_query,
                },
            },
            'layout': {
                'query': self.layout_query,
                'create': self.layout_create,
                'update': self.layout_update,
            },
            'task': {
                'create': self.task_create,
                'query': self.task_query,
                'update': self.task_update,
            },
            'token': {
                'generate': self.token_generate,
                'query': self.token_query,
                'invalidate': self.token_invalidate,
                'update': self.token_update,
            },
        }, **super(Permissions, self).as_dict())
