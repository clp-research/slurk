from calendar import timegm
from flask_login import UserMixin, login_user
from datetime import datetime
import flask_socketio as sio

from .Permissions import Permissions
from .Token import Token
from .database import Database
from .Room import Room, ROOMS
from .Logger import Logger
from .Layout import Layout


logged_users = {}


class User(UserMixin):
    _id = None

    def get_id(self):
        return str(self.id())

    def is_authenticated(self):
        return self.token().valid()

    def id(self):
        return self._id

    def token(self):
        c = Database().get_cursor()
        c.execute("SELECT TokenId FROM User WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        if fetch[0] is None:
            return None
        return Token.from_id(fetch[0])

    def set_token(self, token: Token):
        if not isinstance(token, Token):
            raise TypeError(
                f"Object of type `Token` expected, however type `{type(token)}` was passed")

        db = Database()
        db.get_cursor().execute(
            'UPDATE User SET TokenId = ? WHERE Id = ?;', (token.id(), self.id()))
        db.commit()

    def name(self):
        c = Database().get_cursor()
        c.execute("SELECT Name FROM User WHERE Id = ?;", (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch and fetch[0] else None

    def set_name(self, name: str):
        if not isinstance(name, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(name)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE User SET Name = ? WHERE Id = ?;', (name, self.id()))
        db.commit()

    def sid(self):
        c = Database().get_cursor()
        c.execute(
            'SELECT SessionId FROM SessionId WHERE UserId = ? ORDER BY Updated DESC LIMIT 1;', (self.id(),))
        fetch = c.fetchone()
        return fetch[0] if fetch and fetch[0] else None

    def set_sid(self, sid: str):
        if not isinstance(sid, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(sid)}` was passed")

        db = Database()
        db.get_cursor().execute('INSERT OR REPLACE INTO SessionId(`UserId`, `SessionId`) VALUES(?, ?);',
                                (self.id(), sid))
        db.commit()

    def latest_room(self):
        c = Database().get_cursor()
        c.execute('SELECT LatestRoom FROM User WHERE Id = ?;', (self.id(),))
        fetch = c.fetchone()
        return Room(fetch[0]) if fetch and fetch[0] else None

    def set_latest_room(self, latest_room: Room):
        if not isinstance(latest_room, Room):
            raise TypeError(
                f"Object of type `Room` expected, however type `{type(latest_room)}` was passed")

        db = Database()
        db.get_cursor().execute('UPDATE User SET LatestRoom = ? WHERE Id = ?;',
                                (latest_room.id(), self.id()))
        db.commit()

    def join_room(self, room: Room):
        if not isinstance(room, Room):
            raise TypeError(
                f"Object of type `Room` expected, however type `{type(room)}` was passed")

        db = Database()
        db.get_cursor().execute('INSERT OR REPLACE INTO UserRoom(`UserId`, `RoomId`) VALUES (?, ?);',
                                (self.id(), room.id()))
        db.commit()
        self.set_latest_room(room)
        sio.join_room(room.name(), self.sid())

        if room.id() not in ROOMS:
            ROOMS[room.id()] = {
                'log': Logger('log/{:%Y-%m-%d %H-%M-%S}-{}.log'.format(datetime.now(), room.name())),
                'users': {},
                'listeners': {}
            }

        users = [User.from_id(id).serialize()
                 for id in ROOMS[room.id()]['users']]
        ROOMS[room.id()]['users'][self.id()] = self

        history = []
        for event in ROOMS[room.id()]['log'].get_data():
            if (event["type"] == "new_image" or event["type"] == "text") and ('receiver' not in event or event["receiver"] == self.id()):
                history.append(event)
            if event["type"] == "command" and event["user"]['id'] == self.id():
                history.append(event)

        sio.emit('status', {
            'type': 'join',
            'user': self.serialize(),
            'room': room.serialize(),
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=room.name())

        sio.emit('joined_room', {
            'room': room.serialize(),
            'layout': Layout.from_json_file(room.layout_path()).serialize(),
            'users': users,
            'history': history,
            'self': self.serialize(),
            'permissions': Permissions(self.token(), room).serialize()
        }, room=self.sid())
        ROOMS[room.id()]['log'].append(
            {'type': "join", 'user': self.serialize(), 'room': room.serialize()})
        print(self.name(), "joined room:", room.name())

    def leave_room(self, room: Room):
        if not isinstance(room, Room):
            raise TypeError(
                f"Object of type `Room` expected, however type `{type(room)}` was passed")

        db = Database()
        db.get_cursor().execute(
            'DELETE FROM UserRoom WHERE UserId = ? AND RoomId = ?;', (self.id(), room.id()))
        db.commit()
        sio.leave_room(room.name(), self.sid())
        sio.emit('left_room', {'room': room.serialize()}, room=self.sid())

        ROOMS[room.id()]['log'].append(
            {'type': "leave", 'user': self.serialize(), 'room': room.serialize()})
        print(self.name(), "left room:", room.name())

        if room.id() in ROOMS:
            if self.id() in ROOMS[room.id()]['users']:
                del ROOMS[room.id()]['users'][self.id()]
            if not ROOMS[room.id()]:
                del ROOMS[room.id()]
                sio.close_room(room.name())

        sio.emit('status', {
            'type': 'leave',
            'room': room.serialize(),
            'user': self.serialize(),
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=room.name())

    def rooms(self):
        return [Room(id[0]) for id in Database().get_cursor().execute('SELECT RoomId FROM UserRoom WHERE UserId = ?',
                                                                      (self.id(),))]

    def in_room(self, room: Room):
        if not isinstance(room, Room):
            raise TypeError(
                f"Object of type `Room` expected, however type `{type(room)}` was passed")

        c = Database().get_cursor()
        c.execute('SELECT COUNT(*) FROM UserRoom WHERE UserId = ? AND RoomId = ?',
                  (self.id(), room.id()))
        fetch = c.fetchone()
        return Room(fetch[0]) if fetch[0] else None

    def serialize(self):
        return {
            'id': self.id(),
            'name': self.name(),
            'sid': self.sid(),
            'token': self.token().serialize(),
            'latest_room': self.latest_room().serialize(),
            'rooms': [room.serialize() for room in self.rooms()]
        }

    @classmethod
    def from_id(cls, id):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(
                f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        global logged_users
        if id not in logged_users:
            c = Database().get_cursor()
            c.execute('SELECT COUNT(*) FROM User WHERE Id = ?', (id,))
            logged_users[id] = cls(id) if c.fetchone()[0] != 0 else None
        return logged_users[id]

    @classmethod
    def from_sid(cls, sid: str):
        if not isinstance(sid, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(sid)}` was passed")

        c = Database().get_cursor()
        c.execute('SELECT UserId FROM SessionId WHERE SessionId = ?', (sid,))
        id = c.fetchone()
        return cls(id[0]) if id[0] else None

    @classmethod
    def login(cls, name: str, token: Token):
        if not token:
            return None
        if not isinstance(name, str):
            raise TypeError(
                f"Object of type `str` expected, however type `{type(name)}` was passed")
        if not isinstance(token, Token):
            raise TypeError(
                f"Object of type `Token` expected, however type `{type(token)}` was passed")

        if not token.valid():
            return None

        db = Database()
        c = db.get_cursor()
        c.execute('INSERT INTO User(`TokenId`, `Name`) VALUES (?, ?);',
                  (token.id(), name))
        db.commit()

        user = cls(c.lastrowid)
        login_user(user)
        return user

    def __repr__(self):
        return str(self.serialize())

    def __init__(self, id: int):
        if not isinstance(id, int) and not isinstance(id, str):
            raise TypeError(
                f"Object of type `int` or `str` expected, however type `{type(id)}` was passed")

        self._id = int(id)
