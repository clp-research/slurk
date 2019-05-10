from .. import db

from . import Base
from .token import Token


class Task(Base):
    __tablename__ = 'Task'

    name = db.Column(db.String, nullable=False)
    num_users = db.Column(db.Integer)
    tokens = db.relationship(Token.__tablename__, backref="task")

    def as_dict(self):
        return dict({
            'name': self.name,
            'num_users': self.num_users,
            'tokens': [str(token) for token in self.tokens]
        }, **super(Task, self).as_dict())
