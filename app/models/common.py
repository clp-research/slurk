import calendar

from sqlalchemy import Column, Integer, DateTime, func, Table, ForeignKey, String

from . import Base


class Common(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, default=func.current_timestamp())
    date_modified = Column(
        DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def as_dict(self):
        return {
            'id': self.id,
            'date_created': calendar.timegm(self.date_created.timetuple()),
            'date_modified': calendar.timegm(self.date_modified.timetuple()),
        }


user_room = Table('User_Room', Base.metadata,
                  Column('user_id', Integer, ForeignKey(
                      'User.id', ondelete="CASCADE"),
                      primary_key=True),
                  Column('room_name', String, ForeignKey('Room.name', ondelete="CASCADE"), primary_key=True))
