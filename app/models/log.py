from .. import db

from . import Base

import bson


class Log(Base):
    __tablename__ = 'Log'

    event = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    room_id = db.Column(db.String, db.ForeignKey("Room.name"))
    data = db.Column(db.Binary, nullable=False)

    def as_dict(self):
        base = dict({
            'event': self.event,
            'user': {
                'id': self.user_id,
                'name': self.user.name,
            },
            'room': self.room_id,
            'data': bson.loads(self.data),
        }, **super(Log, self).as_dict())
        return dict(base, **bson.loads(self.data))
