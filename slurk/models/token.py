from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import PickleType, Integer, String

from .common import Common
from .permissions import Permissions


def uuid():
    from uuid import uuid4

    return str(uuid4())


class Token(Common):
    __tablename__ = "Token"

    id = Column(String(length=36), primary_key=True, default=uuid)
    permissions_id = Column(Integer, ForeignKey("Permissions.id"), nullable=False)
    registrations_left = Column(Integer, nullable=False)
    task_id = Column(Integer, ForeignKey("Task.id"))
    room_id = Column(Integer, ForeignKey("Room.id"))
    openvidu_settings = Column(PickleType, nullable=False)

    task = relationship("Task")
    room = relationship("Room")
    users = relationship("User", backref="token")

    def add_user(self, db_session):
        if self.registrations_left == 0:
            raise ValueError("No registrations left for given token")
        if self.registrations_left > 0:
            self.registrations_left -= 1
        db_session.commit()

    @staticmethod
    def get_admin_token(db, id=None):
        with db.create_session() as session:
            token = (
                session.query(Token)
                .filter_by(registrations_left=-1)
                .filter(Token.permissions.has(Permissions.api))
                .first()
            )
            if not token:
                token = Token(
                    id=id,
                    permissions=Permissions(
                        api=True,
                        send_message=False,
                        send_html_message=False,
                        send_image=False,
                        send_command=False,
                        send_privately=False,
                        receive_bounding_box=False,
                        broadcast=False,
                    ),
                    registrations_left=-1,
                    openvidu_settings={},
                )
                session.add(token)
                session.commit()
            return str(token.id)
