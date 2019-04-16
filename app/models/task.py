from .. import db

from . import Base
from .token import Token


class Task(Base):
    __tablename__ = 'Task'

    name = db.Column(db.String, nullable=False)
    num_users = db.Column(db.Integer)
    tokens = db.relationship(Token.__tablename__, backref="task")
