from uuid import uuid4

from sqlalchemy_utils.types.uuid import UUIDType
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from .common import Common


class Token(Common):
    __tablename__ = "Token"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey('User.id'))
    task_id = Column(Integer, ForeignKey('Task.id'))
    room_name = Column(String, ForeignKey('Room.name'))
    room = relationship('Room', lazy='subquery')
    permissions_id = Column(Integer, ForeignKey("Permissions.id"), nullable=False)
    source = Column(String)
    valid = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return str(self.id)

    def as_dict(self):
        return dict({
            'user': self.user_id,
            'task': self.task_id,
            'room': self.room_name,
            'permissions': self.permissions.as_dict(),
            'source': self.source,
            'valid': self.valid,
        }, **super(Token, self).as_dict())
