from sqlalchemy import Column, String, asc, Boolean
from sqlalchemy.orm import relationship

from .common import Common, user_room


class User(Common):
    __tablename__ = 'User'

    name = Column(String)
    token = relationship("Token", backref="user", uselist=False, lazy='joined')
    rooms = relationship("Room", secondary=user_room, back_populates="users", lazy='dynamic')
    session_id = Column(String, unique=True)
    logs = relationship("Log", backref="user", order_by=asc("date_modified"))

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def as_dict(self):
        return dict({
            'name': self.name,
            'token': str(self.token.id),
            'rooms': [room.name for room in self.rooms],
            'session_id': self.session_id,
        }, **super(User, self).as_dict())

    def get_id(self):
        return self.id
