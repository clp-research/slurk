from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Database:
    _engine = None
    _session = sessionmaker()

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

    def bind(self, engine):
        self._engine = engine
        if 'sqlite' in engine.url:
            from logging import getLogger
            from flask.globals import current_app

            if current_app and not current_app.config['DEBUG']:
                getLogger('slurk').warning('SQLite should not be used in production')

            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        self._session.configure(bind=engine)

    def init(self):
        Base.metadata.create_all(bind=self.engine)

    def clear(self):
        Base.metadata.drop_all(bind=self.engine)

    def init_app(self, app):
        from flask import _app_ctx_stack, current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session

        if not self.engine:
            self.bind(engine=create_engine(current_app.config['DATABASE']))

        app.session = scoped_session(
            lambda: self.create_session(), scopefunc=_app_ctx_stack
        )

        self.init()

        @app.teardown_appcontext
        def cleanup(resp_or_exc):
            if current_app.session.is_active:
                current_app.session.remove()


db = Database()


def init_app(app, engine=None):
    if engine:
        db.bind(engine)
    db.init_app(app)
