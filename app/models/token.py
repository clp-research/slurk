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
    permissions_id = Column(Integer, ForeignKey('Permissions.id'), nullable=False)
    logins_left = Column(Integer, nullable=False)
    task_id = Column(Integer, ForeignKey('Task.id'))
    room_id = Column(Integer, ForeignKey('Room.id'))
    openvidu_settings = Column(PickleType, nullable=False)

    task = relationship('Task')
    room = relationship('Room')
    users = relationship('User', backref='token')

    @staticmethod
    def get_admin_token(db, id=None):
        with db.create_session() as session:
            token = session.query(Token).filter_by(logins_left=-1).filter(
                Token.permissions.has(Permissions.api)
            ).one_or_none()
            if not token:
                token = Token(
                    id=id,
                    permissions=Permissions(
                        api=True,
                        send_message=False,
                        send_image=False,
                        send_command=False,
                    ),
                    logins_left=-1,
                    openvidu_settings={}
                )
                session.add(token)
                session.commit()
            return str(token.id)
