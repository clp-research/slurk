from sqlalchemy import event, engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Database:
    _engine = None
    _session = sessionmaker()
    _connect_args = {}
    _poolclass = None

    def __init__(self, app=None, engine=None):
        if engine:
            self.bind(engine)
            self.init()
        if app:
            self.init_app(app)

    @property
    def engine(self):
        return self._engine

    def create_session(self):
        return self._session()

    def apply_driver_hacks(self, url):
        url = engine.url.make_url(url)
        if url.drivername == "sqlite" and url.database in (None, "", ":memory:"):
            from flask.globals import current_app
            from sqlalchemy.pool import StaticPool

            if current_app and not current_app.config["DEBUG"]:
                current_app.logger.warning("SQLite should not be used in production")

            self._connect_args = {"check_same_thread": False}
            self._poolclass = StaticPool

    def bind(self, engine):
        self._engine = engine
        self._session.configure(bind=engine)

        if engine.url.drivername == "sqlite":

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    def init(self):
        Base.metadata.create_all(bind=self.engine)

    def clear(self):
        Base.metadata.drop_all(bind=self.engine)

    def init_app(self, app):
        from flask import _app_ctx_stack, current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session

        if not self.engine:
            self.apply_driver_hacks(current_app.config["DATABASE"])

            self.bind(
                engine=create_engine(
                    current_app.config["DATABASE"],
                    connect_args=self._connect_args,
                    poolclass=self._poolclass,
                )
            )

        app.session = scoped_session(
            lambda: self.create_session(), scopefunc=_app_ctx_stack
        )

        @app.teardown_appcontext
        def cleanup(resp_or_exc):
            if current_app.session.is_active:
                current_app.session.remove()

        self.init()


db = Database()


def init_app(app, engine=None):
    if engine:
        db.bind(engine)
    db.init_app(app)
