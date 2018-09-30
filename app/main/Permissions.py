from .database import Database
from .Room import Room
from .Token import Token


class Permissions:
    _token = None
    _room = None

    def token(self):
        return Token.from_id(self._token)

    def room(self):
        return Room.from_id(self._room)

    def write(self):
        c = Database().get_cursor()
        c.execute("SELECT Write FROM Token_Room_Permissions WHERE TokenId = ? AND RoomId = ?;",
                  (self._token, self._room))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_write(self, write):
        db = Database()
        db.get_cursor().execute('UPDATE Token_Room_Permissions SET Write = ? WHERE TokenId = ? AND RoomId = ?;',
                                (write, self._token, self._room))
        db.commit()

    def see_users(self):
        c = Database().get_cursor()
        c.execute("SELECT ShowUsers FROM Token_Room_Permissions WHERE TokenId = ? AND RoomId = ?;",
                  (self._token, self._room))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_see_users(self, see_users):
        db = Database()
        db.get_cursor().execute('UPDATE Token_Room_Permissions SET ShowUsers = ? WHERE TokenId = ? AND RoomId = ?;',
                                (see_users, self._token, self._room))
        db.commit()

    def see_latency(self):
        c = Database().get_cursor()
        c.execute("SELECT ShowLatency FROM Token_Room_Permissions WHERE TokenId = ? AND RoomId = ?;",
                  (self._token, self._room))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_see_latency(self, see_latency):
        db = Database()
        db.get_cursor().execute('UPDATE Token_Room_Permissions SET ShowLatency = ? WHERE TokenId = ? AND RoomId = ?;',
                                (see_latency, self._token, self._room))
        db.commit()

    def see_input(self):
        c = Database().get_cursor()
        c.execute("SELECT ShowInput FROM Token_Room_Permissions WHERE TokenId = ? AND RoomId = ?;",
                  (self._token, self._room))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_see_input(self, see_input):
        db = Database()
        db.get_cursor().execute('UPDATE Token_Room_Permissions SET ShowInput = ? WHERE TokenId = ? AND RoomId = ?;',
                                (see_input, self._token, self._room))
        db.commit()

    def see_history(self):
        c = Database().get_cursor()
        c.execute("SELECT ShowHistory FROM Token_Room_Permissions WHERE TokenId = ? AND RoomId = ?;",
                  (self._token, self._room))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_see_history(self, see_history):
        db = Database()
        db.get_cursor().execute('UPDATE Token_Room_Permissions SET ShowHistory = ? WHERE TokenId = ? AND RoomId = ?;',
                                (see_history, self._token, self._room))
        db.commit()

    def see_interaction_area(self):
        c = Database().get_cursor()
        c.execute("SELECT ShowInteractionArea FROM Token_Room_Permissions WHERE TokenId = ? AND RoomId = ?;",
                  (self._token, self._room))
        fetch = c.fetchone()
        return fetch[0] != 0 if fetch and fetch[0] else False

    def set_see_interaction_area(self, see_interaction_area):
        db = Database()
        db.get_cursor().execute('UPDATE Token_Room_Permissions SET ShowInteractionArea = ? '
                                'WHERE TokenId = ? AND RoomId = ?;',
                                (see_interaction_area, self._token, self._room))
        db.commit()

    def serialize(self):
        return {
            'write': self.write(),
            'see_users': self.see_users(),
            'see_latency': self.see_latency(),
            'see_input': self.see_input(),
            'see_history': self.see_history(),
            'see_interaction_area': self.see_interaction_area(),
        }

    def __init__(self, token, room):
        if not isinstance(token, Token):
            raise TypeError(f"Object of type `Token` expected, however type `{type(token)}` was passed")
        if not isinstance(room, Room):
            raise TypeError(f"Object of type `Room` expected, however type `{type(room)}` was passed")

        c = Database().get_cursor()
        c.execute('SELECT COUNT(*) FROM Token_Room_Permissions WHERE TokenId = ? and RoomId = ?', (token.id(), room.id()))
        if c.fetchone()[0] == 0:
            room = Room.from_id(room.id())
            write = not room.read_only()

            db = Database()
            c = db.get_cursor()
            c.execute("""INSERT INTO 
                           Token_Room_Permissions(`TokenId`, `RoomId`, `Write`, `ShowUsers`, `ShowLatency`) 
                         VALUES 
                           (?, ?, ?, ?, ?);""",
                      (token.id(), room.id(), write, room.show_users(), room.show_latency()))
            db.commit()

        self._token = token.id()
        self._room = room.id()

    def __repr__(self):
        return str(self.serialize())
