from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .common import Common


class Task(Common):
    __tablename__ = 'Task'

    name = Column(String, nullable=False)
    num_users = Column(Integer)
    layout_id = Column(ForeignKey("Layout.id"))
    tokens = relationship('Token', backref="task")

    def as_dict(self):
        return dict({
            'name': self.name,
            'num_users': self.num_users,
            'layout': self.layout_id,
            'tokens': [str(token) for token in self.tokens]
        }, **super(Task, self).as_dict())
