from uuid import uuid4

from .Room import Room
from .Task import Task
from .database import Database


class Token:
    _id = None

    def id(self):
        return self._id

    def task(self):
        c = Database().get_cursor()
        c.execute("SELECT TaskId FROM Token WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return Task(fetch[0]) if fetch[0] else None

    def set_task(self, task):
        if not isinstance(task, Task):
            raise TypeError(f"Object of type `Task` expected, however type `{type(task)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Token SET TaskId = ? WHERE Id = ?;', (task.id(), self.id()))
        db.commit()

    def uuid(self):
        c = Database().get_cursor()
        c.execute("SELECT Uuid FROM Token WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch[0] else None

    def set_uuid(self, uuid):
        if not isinstance(uuid, str):
            raise TypeError(f"Object of type `str` expected, however type `{type(uuid)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Token SET Uuid = ? WHERE Id = ?;', (uuid, self.id()))
        db.commit()

    def url(self):
        c = Database().get_cursor()
        c.execute("SELECT Url FROM Token WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch[0] else None

    def set_url(self, url):
        if not isinstance(url, str):
            raise TypeError(f"Object of type `str` expected, however type `{type(url)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Token SET Url = ? WHERE Id = ?;', (url, self.id()))
        db.commit()

    def time(self):
        c = Database().get_cursor()
        c.execute("SELECT `Time` FROM Token WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch[0] else None

    def set_time(self, time):
        if not isinstance(time, str):
            raise TypeError(f"Object of type `str` expected, however type `{type(time)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Token SET `Time` = ? WHERE Id = ?;', (time, self.id()))
        db.commit()

    def room(self):
        c = Database().get_cursor()
        c.execute("SELECT Room FROM Token WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()

        if fetch[0] is None:
            return None
        return Room(fetch[0])

    def set_room(self, room):
        if not isinstance(room, Room):
            raise TypeError(f"Object of type `Room` expected, however type `{type(room)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Token SET Room = ? WHERE Id = ?;', (room.id(), self.id()))
        db.commit()

    def valid(self):
        c = Database().get_cursor()
        c.execute("SELECT Valid FROM Token WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch[0] else None

    def invalidate(self):
        db = Database()
        db.get_cursor().execute('UPDATE Token SET Valid = 0 WHERE Id = ?;', (self.id(),))
        db.commit()

    def serialize(self):
        task = self.task()
        return {
            'id': self.id(),
            'task': task.serialize() if task else None,
            'uuid': self.uuid(),
            'time': self.time(),
            'room': self.room().serialize(),
            'valid': self.valid(),
        }

    @classmethod
    def from_id(cls, id):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        c = Database().get_cursor()
        c.execute("SELECT COUNT(*) FROM Token WHERE Id = ?;", (id,))
        if not c.fetchone():
            return None
        return cls(id)

    @classmethod
    def from_uuid(cls, uuid):
        if not isinstance(uuid, str):
            raise TypeError(f"Object of type `str` expected, however type `{type(uuid)}` was passed")

        c = Database().get_cursor()
        c.execute("SELECT Id FROM Token WHERE Uuid = ?;", (uuid,))
        fetch = c.fetchone()
        if not fetch:
            return None
        return cls(fetch[0])

    @classmethod
    def create(cls, url, initial_room, task):
        if not isinstance(url, str):
            raise TypeError(f"Object of type `str` expected, however type `{type(url)}` was passed")
        if not isinstance(initial_room, Room):
            raise TypeError(f"Object of type `Room` expected, however type `{type(initial_room)}` was passed")
        if not isinstance(task, Task):
            raise TypeError(f"Object of type `Task` expected, however type `{type(task)}` was passed")

        db = Database()
        c = db.get_cursor()
        uuid = str(uuid4())
        c.execute('INSERT INTO Token(`Uuid`, `Url`, `Room`, `TaskId`) VALUES (?, ?, ?, ?);',
                  (uuid, url, initial_room.id(), task.id() if task.name() != "None" else None))
        db.commit()
        return cls(c.lastrowid)

    def __init__(self, id):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        self._id = int(id)

    def __repr__(self):
        return str(self.serialize())
