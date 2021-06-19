from datetime import datetime

from sqlalchemy import Column, String, ForeignKey
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

        from app.views.api.openvidu.schemas import WebRtcConnectionSchema
        from app.extensions.events import socketio
        from app.models.room import Session

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
                timestamp=str(datetime.utcnow())
            ), room=str(room.id))

            Log.add("join", self, room)

            # Create an OpenVidu connection if apropiate
            if hasattr(current_app, 'openvidu') and room.openvidu_session_id and self.token.permissions.openvidu_role:
                # OpenVidu destroys a session when everyone left.
                # This ensures, that the session is persistant by recreating the session
                def post_connection(retry=True):
                    response = current_app.openvidu.post_connection(room.openvidu_session_id, json={
                        'role': self.token.permissions.openvidu_role
                    })
                    if response.status_code == 200:
                        socketio.emit('openvidu', dict(
                            connection=WebRtcConnectionSchema.Response().dump(response.json()),
                            start_with_audio=room.layout.start_with_audio,
                            start_with_video=room.layout.start_with_video,
                            video_resolution=room.layout.video_resolution,
                            video_framerate=room.layout.video_framerate,
                        ), room=self.session_id)
                    elif response.status_code == 404:
                        json = room.session.parameters
                        json['customSessionId'] = room.session.id
                        response = current_app.openvidu.post_session(json)
                        if response.status_code == 200:
                            post_connection(retry=False)
                        else:
                            current_app.logger.error(response.json().get('message'))
                    else:
                        current_app.logger.error(response.json().get('message'))

                post_connection()

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
            timestamp=str(datetime.utcnow())
        ), room=str(room.id))
