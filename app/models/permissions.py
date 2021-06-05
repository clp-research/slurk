from sqlalchemy import Column, Boolean
from sqlalchemy.orm import relationship

from .common import Common


class Permissions(Common):
    __tablename__ = 'Permissions'

    tokens = relationship('Token', backref='permissions')
    api = Column(Boolean, nullable=False, default=False)
    send_message = Column(Boolean, nullable=False, default=False)
    send_image = Column(Boolean, nullable=False, default=False)
    send_command = Column(Boolean, nullable=False, default=False)
