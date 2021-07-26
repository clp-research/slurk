from datetime import datetime

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from .common import Common, user_room
from .log import Log


class User(Common):
    __tablename__ = "User"

    name = Column(String, nullable=False)
    token_id = Column(String, ForeignKey("Token.id"), nullable=False)
    session_id = Column(String, unique=True)
    rooms = relationship(
        "Room", secondary=user_room, back_populates="users", lazy="dynamic"
    )

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

        from slurk.views.api.openvidu.schemas import WebRtcConnectionSchema
        from slurk.extensions.events import socketio

        if self not in room.users:
            room.users.append(self)
            current_app.session.commit()

        if self.session_id is not None:
            join_room(str(room.id), self.session_id, "/")

            def joined():
                current_app.session.add(self)
                current_app.session.add(room)

                socketio.emit(
                    "status",
                    dict(
                        type="join",
                        user=dict(id=self.id, name=self.name),
                        room=str(room.id),
                        timestamp=str(datetime.utcnow()),
                    ),
                    room=str(room.id),
                )

                Log.add("join", self, room)

                # Create an OpenVidu connection if apropiate
                if (
                    hasattr(current_app, "openvidu")
                    and room.openvidu_session_id
                    and self.token.permissions.openvidu_role
                ):

                    def ov_property(name):
                        if name in self.token.openvidu_settings:
                            return self.token.openvidu_settings[name]
                        else:
                            return room.layout.openvidu_settings[name]

                    # OpenVidu destroys a session when everyone left.
                    # This ensures, that the session is persistant by recreating the session
                    def post_connection(retry=True):
                        response = current_app.openvidu.post_connection(
                            room.openvidu_session_id,
                            json=dict(
                                role=self.token.permissions.openvidu_role,
                                kurentoOptions=dict(
                                    videoMaxRecvBandwidth=ov_property(
                                        "video_max_recv_bandwidth"
                                    ),
                                    videoMinRecvBandwidth=ov_property(
                                        "video_min_recv_bandwidth"
                                    ),
                                    videoMaxSendBandwidth=ov_property(
                                        "video_max_send_bandwidth"
                                    ),
                                    videoMinSendBandwidth=ov_property(
                                        "video_min_send_bandwidth"
                                    ),
                                    allowedFilters=ov_property("allowed_filters"),
                                ),
                            ),
                        )

                        if response.status_code == 200:
                            socketio.emit(
                                "openvidu",
                                dict(
                                    connection=WebRtcConnectionSchema.Response().dump(
                                        response.json()
                                    ),
                                    start_with_audio=ov_property("start_with_audio"),
                                    start_with_video=ov_property("start_with_video"),
                                    video_resolution=ov_property("video_resolution"),
                                    video_framerate=ov_property("video_framerate"),
                                    video_publisher_location=ov_property(
                                        "video_publisher_location"
                                    ),
                                    video_subscribers_location=ov_property(
                                        "video_subscribers_location"
                                    ),
                                ),
                                room=self.session_id,
                            )
                        elif response.status_code == 404:
                            json = room.session.parameters
                            json["customSessionId"] = room.session.id
                            response = current_app.openvidu.post_session(json)
                            if response.status_code == 200:
                                post_connection(retry=False)
                            else:
                                current_app.logger.error(response.json().get("message"))
                        else:
                            current_app.logger.error(response.json().get("message"))

                    post_connection()

            socketio.emit(
                "joined_room",
                {
                    "room": str(room.id),
                    "user": self.id,
                },
                room=self.session_id,
                callback=joined,
            )

    def leave_room(self, room, event_only=False):
        from flask.globals import current_app
        from flask_socketio import leave_room

        from slurk.extensions.events import socketio

        if self in room.users and not event_only:
            room.users.remove(self)
            current_app.session.commit()

        if self.session_id is not None:
            Log.add("leave", self, room)

            socketio.emit(
                "left_room",
                {
                    "room": room.id,
                    "user": self.id,
                },
                room=self.session_id,
            )

            leave_room(str(room.id), self.session_id, "/")

        socketio.emit(
            "status",
            dict(
                type="leave",
                user=dict(id=self.id, name=self.name),
                room=room.id,
                timestamp=str(datetime.utcnow()),
            ),
            room=str(room.id),
        )
