from .database import Database
from .Layout import Layout

ROOMS = dict()


class Room:
    _id = None

    def id(self):
        return self._id

    def name(self):
        c = Database().get_cursor()
        c.execute("SELECT Name FROM Room WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch and fetch[0] else None

    def set_name(self, name):
        if not isinstance(name, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(name)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Room SET Name = ? WHERE Id = ?;', (name, self.id()))
        db.commit()

    def label(self):
        c = Database().get_cursor()
        c.execute("SELECT Label FROM Room WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch and fetch[0] else None

    def set_label(self, label):
        if not isinstance(label, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(label)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Room SET Label = ? WHERE Id = ?;', (label, self.id()))
        db.commit()

    def layout_path(self):
        c = Database().get_cursor()
        c.execute("SELECT Layout FROM Room WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch and fetch[0] else None

    def set_layout_path(self, layout):
        if not isinstance(layout, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(layout)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Room SET Layout = ? WHERE Id = ?;', (layout, self.id()))
        db.commit()

    def read_only(self):
        c = Database().get_cursor()
        c.execute("SELECT ReadOnly FROM Room WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_read_only(self, read_only):
        if not isinstance(read_only, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(read_only)}` was passed")

        db = Database()
        db.get_cursor().execute(
            'UPDATE Room SET ReadOnly = ? WHERE Id = ?;', (read_only, self.id()))
        db.commit()

    def show_users(self):
        c = Database().get_cursor()
        c.execute("SELECT ShowUsers FROM Room WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_show_users(self, show_users):
        if not isinstance(show_users, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(show_users)}` was passed")

        db = Database()
        db.get_cursor().execute(
            'UPDATE Room SET ShowUsers = ? WHERE Id = ?;', (show_users, self.id()))
        db.commit()

    def show_latency(self):
        c = Database().get_cursor()
        c.execute("SELECT ShowLatency FROM Room WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_show_latency(self, show_latency):
        if not isinstance(show_latency, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(show_latency)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Room SET ShowLatency = ? WHERE Id = ?;',
                                (show_latency, self.id()))
        db.commit()

    def static(self):
        c = Database().get_cursor()
        c.execute("SELECT Static FROM Room WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch and fetch[0] else None

    def set_static(self, static):
        if not isinstance(static, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(static)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE Room SET Static = ? WHERE Id = ?;', (static, self.id()))
        db.commit()

    def serialize(self):
        return {
            'id': self.id(),
            'name': self.name(),
            'label': self.label(),
            'layout_path': self.layout_path(),
            'read_only': self.read_only(),
            'show_users': self.show_users(),
            'show_latency': self.show_latency(),
        }

    @classmethod
    def from_id(cls, id):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(
                f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        c = Database().get_cursor()
        c.execute('SELECT COUNT(*) FROM Room WHERE Id = ?', (int(id),))
        return cls(id) if c.fetchone()[0] != 0 else None

    @classmethod
    def create(cls, name, label, layout="", read_only=False, show_users=True, show_latency=True, show_input=True, show_history=True, show_interaction_area=True, static=False):
        if not isinstance(name, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(name)}` was passed")
        if not isinstance(label, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(label)}` was passed")
        if not isinstance(layout, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(layout)}` was passed")
        if not isinstance(read_only, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(read_only)}` was passed")
        if not isinstance(show_users, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(show_users)}` was passed")
        if not isinstance(show_latency, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(show_latency)}` was passed")
        if not isinstance(show_input, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(show_input)}` was passed")
        if not isinstance(show_history, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(show_history)}` was passed")
        if not isinstance(show_interaction_area, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(show_interaction_area)}` was passed")
        if not isinstance(static, bool):
            raise TypeError(
                f"Object of type `bool` expected, however type `{type(static)}` was passed")

        db = Database()
        c = db.get_cursor()
        c.execute('INSERT OR REPLACE INTO Room(`Name`, `Label`, `Layout`, `ReadOnly`, `ShowUsers`, `ShowLatency`, `ShowInput`, `ShowHistory`, `ShowInteractionArea`, `Static`) '
                  'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (name, label, layout, read_only, show_users, show_latency, show_input, show_history, show_interaction_area, static))
        db.commit()
        c.execute("SELECT Id FROM Room WHERE Name = ?;", (name,))
        fetch = c.fetchone()
        return cls(fetch[0]) if fetch and fetch[0] else None

    @classmethod
    def list(cls):
        c = Database().get_cursor()

        rooms = []
        for row in c.execute('SELECT Id FROM Room WHERE Static = 1'):
            rooms.append(cls(row[0]))
        return rooms

    def __init__(self, id):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(
                f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        self._id = int(id)

    def __repr__(self):
        return str(self.serialize())
