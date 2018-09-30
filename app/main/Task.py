from .database import Database


class Task:
    _id = None

    def id(self):
        return self._id

    def users(self):
        c = Database().get_cursor()
        c.execute("SELECT Users FROM Task WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return int(fetch[0]) if fetch[0] else None

    def set_users(self, users):
        if not isinstance(users, int):
            raise TypeError(f"Object of type `int` expected, however type `{type(users)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Task SET Users = ? WHERE Id = ?;', (users, self.id()))
        db.commit()

    def name(self):
        c = Database().get_cursor()
        c.execute("SELECT Name FROM Task WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch[0] else None

    def set_name(self, name):
        if not isinstance(name, str):
            raise TypeError(f"Object of type `str` expected, however type `{type(name)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Task SET Name = ? WHERE Id = ?;', (name, self.id()))
        db.commit()

    def serialize(self):
        return {
            'id': self.id(),
            'users': self.users(),
            'name': self.name(),
        }

    @classmethod
    def from_id(cls, id):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        c = Database().get_cursor()
        c.execute("SELECT COUNT(*) FROM Task WHERE Id = ?;", (id,))
        if not c.fetchone():
            return None
        return cls(id)

    @classmethod
    def list(cls):
        return [cls(row[0]) for row in Database().get_cursor().execute('SELECT Id FROM Task')]

    def __repr__(self):
        return str(self.serialize())

    def __init__(self, id):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        self._id = int(id)
