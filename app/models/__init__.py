import calendar

from .. import db


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def as_dict(self):
        return {
            'id': self.id,
            'date_created': calendar.timegm(self.date_created.timetuple()),
            'date_modified': calendar.timegm(self.date_modified.timetuple()),
        }


user_room = db.Table('User_Room', Base.metadata,
                     db.Column('user_id', db.Integer, db.ForeignKey('User.id', ondelete="CASCADE"), primary_key=True),
                     db.Column('room_name', db.String, db.ForeignKey('Room.name', ondelete="CASCADE"), primary_key=True))
current_user_room = db.Table('User_Room_current', Base.metadata,
                             db.Column('user_id', db.Integer, db.ForeignKey('User.id', ondelete="CASCADE"), primary_key=True),
                             db.Column('room_name', db.String, db.ForeignKey('Room.name', ondelete="CASCADE"), primary_key=True))
