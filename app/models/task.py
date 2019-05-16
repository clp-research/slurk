from .. import db

from . import Base
from .token import Token


class Task(Base):
    __tablename__ = 'Task'

    name = db.Column(db.String, nullable=False)
    num_users = db.Column(db.Integer)
    layout_id = db.Column(db.ForeignKey("Layout.id"))
    tokens = db.relationship(Token.__tablename__, backref="task")

    def as_dict(self):
        return dict({
            'name': self.name,
            'num_users': self.num_users,
            'layout': self.layout_id,
            'tokens': [str(token) for token in self.tokens]
        }, **super(Task, self).as_dict())
