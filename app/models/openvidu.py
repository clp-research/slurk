from sqlalchemy import Column, Boolean, String, Integer, ForeignKey, asc
from sqlalchemy.orm import relationship

from .common import Common


class OpenViduSession(Common):
    __tablename__ = 'OpenViduSession'

    audio = Column(Boolean, default=False, nullable=False)
    video = Column(Boolean, default=False, nullable=False)
    room = relationship("Room", backref="openvidu", uselist=False)
    session_id = Column(String)

    def as_dict(self):
        return {
            'id': self.id,
            'audio': self.audio,
            'video': self.video,
        }
