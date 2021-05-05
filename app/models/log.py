import bson

from sqlalchemy import String, Integer, ForeignKey, LargeBinary, Column

from .common import Common


class Log(Common):
    __tablename__ = 'Log'

    event = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    room_id = Column(String, ForeignKey("Room.name"))
    data = Column(LargeBinary, nullable=False)

    def as_dict(self):
        base = dict({
            'event': self.event,
            'user': {
                'id': self.user_id,
                'name': self.user.name,
                'token': self.user.token.id
            },
            'room': self.room_id,
            'data': bson.loads(self.data),
        }, **super(Log, self).as_dict())
        return dict(base, **bson.loads(self.data))
