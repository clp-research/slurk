from sqlalchemy import String, Integer, ForeignKey, JSON, Column
from sqlalchemy.orm import relationship

from .common import Common


class Log(Common):
    __tablename__ = 'Log'

    event = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id", ondelete='CASCADE'))
    room_id = Column(Integer, ForeignKey("Room.id", ondelete='CASCADE'))
    receiver_id = Column(Integer, ForeignKey("User.id", ondelete='CASCADE'))
    data = Column(JSON, nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    def add(event, user=None, room=None, data=None):
        from flask.globals import current_app

        if not data:
            data = {}

        if event == "join":
            current_app.logger.info(f'{user.name} joined {room.layout.title}')
        if event == "leave":
            current_app.logger.info(f'{user.name} left {room.layout.title})')
        if event == "connect":
            current_app.logger.info(f'{user.name} connected')
        if event == "disconnect":
            current_app.logger.info(f'{user.name} disconnected')

        receiver = data.pop('receiver', None)
        log = Log(event=event, user=user, room=room, data=data, receiver=receiver)

        db = current_app.session
        db.add(log)
        db.commit()
        return log
