from .. import db

from . import Base
from .token import Token


class Task(Base):
    __tablename__ = 'Task'

    name = db.Column(db.String, nullable=False)
    num_users = db.Column(db.Integer)
    tokens = db.relationship(Token.__tablename__, backref="task")

    def __repr__(self):
        return "<Task(name='%s', num_users='%s')>" % (self.name, self.num_users)
