from sqlalchemy import event
from sqlalchemy.engine import Engine

from .layout import Layout
from .log import Log
from .room import Room
from .task import Task
from .token import Token
from .user import User
from .permissions import Permissions


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
