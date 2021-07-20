from sqlalchemy import Column, Boolean, String
from sqlalchemy.orm import relationship

from .common import Common


class Permissions(Common):
    __tablename__ = "Permissions"

    tokens = relationship("Token", backref="permissions")
    api = Column(Boolean, nullable=False)
    send_message = Column(Boolean, nullable=False)
    private_message = Column(Boolean, nullable=False)
    send_image = Column(Boolean, nullable=False)
    send_command = Column(Boolean, nullable=False)
    openvidu_role = Column(String)
