from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .common import Common


class Task(Common):
    __tablename__ = 'Task'

    name = Column(String, nullable=False)
    num_users = Column(Integer, nullable=False)
    layout_id = Column(ForeignKey("Layout.id"), nullable=False)
