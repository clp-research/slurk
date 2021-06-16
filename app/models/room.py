from sqlalchemy import Column, Boolean, Integer, ForeignKey, asc
from sqlalchemy.orm import relationship

from .common import user_room, Common


class Room(Common):
    __tablename__ = 'Room'

    layout_id = Column(Integer, ForeignKey("Layout.id"), nullable=False)
    users = relationship("User", secondary=user_room, back_populates="rooms")
    logs = relationship("Log", backref="room", order_by=asc("date_modified"))
