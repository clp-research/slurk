from uuid import uuid4

from sqlalchemy_utils.types.uuid import UUIDType

from .. import db, socketio

from . import Base
from .permission import Permissions


class Token(Base):
    __tablename__ = "Token"

    id = db.Column(UUIDType(binary=False), default=uuid4, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('Task.id'))
    room_name = db.Column(db.String, db.ForeignKey('Room.name'), nullable=False)
    permissions_id = db.Column(db.Integer, db.ForeignKey(Permissions.id), nullable=False)
    source = db.Column(db.String)
    valid = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return str(self.id)

    def invalidate(self):
        self.valid = False
