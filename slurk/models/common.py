from sqlalchemy import Column, Integer, DateTime, func, Table, ForeignKey

from slurk.extensions.database import Base


class Common(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=func.current_timestamp(), nullable=False)
    date_modified = Column(DateTime, onupdate=func.current_timestamp())


user_room = Table('User_Room', Base.metadata,
                  Column('user_id', Integer, ForeignKey('User.id', ondelete="CASCADE"), primary_key=True),
                  Column('room_id', Integer, ForeignKey('Room.id', ondelete="CASCADE"), primary_key=True))
