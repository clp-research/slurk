from calendar import timegm
from datetime import datetime

from sqlalchemy import Column, String, asc, ForeignKey
from sqlalchemy.orm import relationship

from .common import Common, user_room
from .log import Log


class User(Common):
    __tablename__ = 'User'

    name = Column(String, nullable=False)
    token_id = Column(String, ForeignKey('Token.id'), nullable=False)
    session_id = Column(String, unique=True)
    rooms = relationship("Room", secondary=user_room, back_populates="users", lazy='dynamic')

    # Required by flask_login
    @property
    def is_active(self):
        return True

    # Required by flask_login
    @property
    def is_authenticated(self):
        return True

    # Required by flask_login
    @property
    def is_anonymous(self):
        return False

    # Required by flask_login
    def get_id(self):
        return self.id

    def join_room(self, room):
        from flask.globals import current_app
        from flask_socketio import join_room

        from app.extensions.events import socketio

        if self not in room.users:
            room.users.append(self)
            current_app.session.commit()

        if self.session_id is not None:
            join_room(str(room.id), self.session_id, '/')

            socketio.emit('joined_room', {
                'room': str(room.id),
                'user': self.id,
            }, room=self.session_id)

            socketio.emit('status', dict(
                type='join',
                user=dict(
                    id=self.id,
                    name=self.name),
                room=str(room.id),
                timestamp=timegm(datetime.now().utctimetuple())
            ), room=str(room.id))

            Log.add("join", self, room)

    def leave_room(self, room, event_only=False):
        from flask.globals import current_app
        from flask_socketio import leave_room

        from app.extensions.events import socketio

        if self in room.users and not event_only:
            room.users.remove(self)
            current_app.session.commit()

        if self.session_id is not None:
            Log.add("leave", self, room)

            socketio.emit('left_room', {
                'room': str(room.id),
                'user': self.id,
            }, room=self.session_id)

            leave_room(str(room.id), self.session_id, '/')

        socketio.emit('status', dict(
            type='leave',
            user=dict(
                id=self.id,
                name=self.name),
            room=str(room.id),
            timestamp=timegm(datetime.now().utctimetuple())
        ), room=str(room.id))
