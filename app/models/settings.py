from .. import db

from . import Base


class Settings(Base):
    __tablename__ = 'Room'

    name = db.Column(db.String, nullable=False, unique=True)
    setting = db.Column(db.String)
