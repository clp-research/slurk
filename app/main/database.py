import sqlite3
from flask import g

from .. import config


class Database:
    def __init__(self):
        self.db = getattr(g, '_database', None)
        self._database_name = getattr(g, '_database_name', None)
        if not self._database_name:
            database_name = config["server"].get("database")
            if not database_name:
                print(
                    "WARNING: No database specified in config. Using default name: `botsi.db`")
                database_name = "botsi.db"
            setattr(g, "_database_name", database_name)
        if self.db is None:
            self.db = g._database = sqlite3.connect(
                database_name, timeout=10)
            self._ensure_database()

    def _ensure_database(self):
        c = self.db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS User
                    (
                        Id         INTEGER PRIMARY KEY AUTOINCREMENT,
                        TokenId    INTEGER NOT NULL
                                     CONSTRAINT TokenId_fk
                                     REFERENCES Token(Id)
                                       ON UPDATE CASCADE
                                       ON DELETE CASCADE,
                        Name       TEXT NOT NULL,
                        LatestRoom INTEGER
                                     CONSTRAINT LatestRoom_fk
                                     REFERENCES Room(Id)
                                       ON UPDATE CASCADE
                                       ON DELETE CASCADE,
                        Created    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );""")

        c.execute("""CREATE TABLE IF NOT EXISTS Task
                     (
                        Id    INTEGER PRIMARY KEY AUTOINCREMENT,
                        Users INTEGER NOT NULL,
                        Name  TEXT NOT NULL
                     );""")
        c.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS Task_Name_idx ON Task(Name);""")

        c.execute("""CREATE TABLE IF NOT EXISTS Room
                     (
                       Id           INTEGER PRIMARY KEY AUTOINCREMENT,
                       Name         TEXT NOT NULL,
                       Label        TEXT NOT NULL,
                       Layout       TEXT,
                       ReadOnly     INTEGER DEFAULT 0 NOT NULL,
                       ShowUsers    INTEGER DEFAULT 1 NOT NULL,
                       ShowLatency  INTEGER DEFAULT 1 NOT NULL,
                       ShowInput    INTEGER DEFAULT 1 NOT NULL,
                       ShowHistory  INTEGER DEFAULT 1 NOT NULL,
                       ShowInteractionArea INTEGER DEFAULT 1 NOT NULL,
                       Static       INTEGER DEFAULT 0 NOT NULL
                     );""")
        c.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS Room_Name_idx ON Room(Name);""")

        c.execute("""CREATE TABLE IF NOT EXISTS UserRoom
                     (
                       UserId  INTEGER NOT NULL
                                 CONSTRAINT UserId_fk
                                 REFERENCES User(Id)
                                   ON UPDATE CASCADE
                                   ON DELETE CASCADE,
                       RoomId  INTEGER NOT NULL
                                 CONSTRAINT RoomId_fk
                                 REFERENCES Room(Id)
                                   ON UPDATE CASCADE
                                   ON DELETE CASCADE,
                       Joined  TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                     );""")
        c.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS User_Name_idx ON UserRoom(UserId, RoomId);""")

        c.execute("""CREATE TABLE IF NOT EXISTS SessionId
                     (
                       Id        INTEGER PRIMARY KEY AUTOINCREMENT,
                       UserId    INTEGER NOT NULL
                                   CONSTRAINT UserId_fk
                                   REFERENCES User(Id)
                                     ON UPDATE CASCADE
                                     ON DELETE CASCADE,
                       SessionId TEXT NOT NULL,
                       Updated   TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                     );""")
        c.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS SessionId_idx ON SessionId(SessionId);""")

        c.execute("""CREATE TABLE IF NOT EXISTS Token_Room_Permissions
                     (
                       TokenId    INTEGER NOT NULL
                                    CONSTRAINT TokenId_fk
                                    REFERENCES Token(Id)
                                      ON UPDATE CASCADE
                                      ON DELETE CASCADE,
                       RoomId     INTEGER NOT NULL
                                    CONSTRAINT RoomId_fk
                                    REFERENCES Room(Id)
                                      ON UPDATE CASCADE
                                      ON DELETE CASCADE,
                       Updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                       Write      INTEGER DEFAULT 1 NOT NULL,
                       ShowUsers   INTEGER DEFAULT 1 NOT NULL,
                       ShowLatency INTEGER DEFAULT 1 NOT NULL,
                       ShowInput INTEGER DEFAULT 1 NOT NULL,
                       ShowHistory INTEGER DEFAULT 1 NOT NULL,
                       ShowInteractionArea INTEGER DEFAULT 1 NOT NULL
                     );""")
        c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS Token_Room_Permissions_idx
                     ON Token_Room_Permissions(TokenId, RoomId);""")

        c.execute("""CREATE TABLE IF NOT EXISTS Token
                     (
                       Id        INTEGER PRIMARY KEY AUTOINCREMENT,
                       TaskId    INTEGER
                                   CONSTRAINT TaskId_fk
                                   REFERENCES Task(Id)
                                     ON UPDATE CASCADE
                                     ON DELETE CASCADE,
                       Uuid      TEXT NOT NULL,
                       Url       TEXT NOT NULL,
                       Time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                       Room      INTEGER NOT NULL
                                   CONSTRAINT RoomId_fk
                                   REFERENCES Room(Id)
                                     ON UPDATE CASCADE
                                     ON DELETE CASCADE,
                       Valid     INTEGER DEFAULT 1 NOT NULL
                     );""")
        c.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS Token_Uuid_idx ON Token(Uuid);""")

        self.create_task("meetup", 2)
        self.create_task("None", -1)
        self.create_room("Waiting Room", layout="waiting_room",
                         read_only=True, show_users=False, show_latency=False)
        self.create_room("Test Room", layout="test_room",
                         read_only=False, show_users=True, show_latency=True)
        self.db.commit()

    def get_cursor(self):
        return self.db.cursor()

    def commit(self):
        self.db.commit()

    def tasks(self):
        c = self.db.cursor()

        d = {}
        for row in c.execute('SELECT Id, Users, Name FROM Task'):
            d[row[0]] = (row[1], row[2])
        return d

    def task_list(self):
        c = self.db.cursor()

        d = []
        for row in c.execute('SELECT Name FROM Task'):
            d.append((row[0], row[0]))
        return d

    def create_task(self, name, required_users):
        c = self.db.cursor()
        c.execute('INSERT OR IGNORE INTO Task(`Name`, `Users`) VALUES (?, ?);',
                  (name, required_users))
        self.db.commit()

    def create_room(self, name, layout="", read_only=False, show_users=True, show_latency=True, show_input=True, show_history=True, show_interaction_area=True):
        c = self.db.cursor()
        c.execute('SELECT COUNT(*) FROM Room WHERE Name = ?', (name,))
        if c.fetchone()[0] == 0:
            c.execute('INSERT OR IGNORE INTO '
                      'Room(`Name`, `Label`, `Layout`, `ReadOnly`, `ShowUsers`, `ShowLatency`, `ShowInput`, `ShowHistory`, `ShowInteractionArea`, `Static`) '
                      'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);', (name, name, layout, read_only, show_users, show_latency, show_input, show_history, show_interaction_area))
            self.db.commit()

    def rooms(self):
        c = self.db.cursor()

        d = []
        for row in c.execute('SELECT Name FROM Room'):
            d.append((row[0], row[0]))
        return d

    def user_matches_token(self, name, token):
        c = self.db.cursor()

        c.execute('SELECT Id, Used, Reuseable FROM Token WHERE Uuid = ?', (token,))
        fetch = c.fetchone()

        if not fetch:
            return False

        id = fetch[0]
        used = fetch[1]
        reuseable = fetch[2]

        if not used:
            return True
        if used and not reuseable:
            return False

        # reuseable and used:
        c.execute(
            'SELECT COUNT(*) FROM User WHERE TokenId = ? AND Name = ?', (id, name))
        return c.fetchone()[0] != 0

    def user_exist(self, id):
        c = self.db.cursor()
        c.execute('SELECT COUNT(*) FROM User WHERE Id = ?', (id,))
        return c.fetchone()[0] != 0

    def user_id(self, name, token):
        c = self.db.cursor()

        if not self.user_matches_token(name, token):
            return None

        c.execute(
            'UPDATE Token SET Used = 1 WHERE Uuid = ? AND (Used = 0 OR Reuseable != 0);', (token,))
        if c.rowcount != 1:
            return None
        c.execute('SELECT Id FROM Token WHERE Uuid = ?', (token,))
        token_id = c.fetchone()
        if not token_id:
            return None
        c.execute('SELECT Id FROM User WHERE TokenId = ?', (token_id[0],))
        user_id = c.fetchone()
        if user_id:
            return user_id[0]
        c.execute('INSERT INTO User(`TokenId`, `Name`) VALUES (?, ?);',
                  (token_id[0], name))
        self.db.commit()
        return c.lastrowid
