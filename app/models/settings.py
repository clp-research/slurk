from .. import db

from . import Base


class Settings(Base):
    __tablename__ = 'Room'

    name = db.Column(db.String, nullable=False, unique=True)
    setting = db.Column(db.String)

    def __repr__(self):
        return "<Room(name='%s', label='%s', layout='%s')>" % (self.name, self.label, self.layout)
