from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, asc
from sqlalchemy.orm import relationship

from . import Base
from .common import user_room


class Room(Base):
    __tablename__ = 'Room'

    name = Column(String, primary_key=True)
    label = Column(String, nullable=False)
    layout_id = Column(Integer, ForeignKey("Layout.id"), nullable=False)
    read_only = Column(Boolean, default=False, nullable=False)
    show_users = Column(Boolean, default=True, nullable=False)
    show_latency = Column(Boolean, default=True, nullable=False)
    static = Column(Boolean, default=False, nullable=False)
    users = relationship("User", secondary=user_room, back_populates="rooms")
    logs = relationship("Log", backref="room", order_by=asc("date_modified"))

    def as_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'layout': self.layout_id,
            'read_only': self.read_only,
            'show_users': self.show_users,
            'show_latency': self.show_latency,
            'static': self.static,
            'users': {user.id: user.name for user in self.users},
        }
