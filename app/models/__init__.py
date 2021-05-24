from logging import getLogger

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()   # NOQA

from .layout import Layout
from .log import Log
from .permission import Permissions
from .room import Room
from .task import Task
from .token import Token
from .user import User


class Model:
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
        getLogger('slurk').debug("Created database session")
        return self._session()

    def bind(self, engine):
        self._engine = engine
        self._session.configure(bind=engine)

    def init(self):
        Base.metadata.create_all(bind=self.engine)

    def clear(self):
        Base.metadata.drop_all(bind=self.engine)

    def generate_admin_token(self, token=None, api_token=True):
        token_id = None
        if not api_token:
            room = Room(name='admin_room',
                        label='Admin Room',
                        layout=Layout.from_json_file('default'))
        else:
            room = None

        with self.create_session() as session:
            token_data = Token(
                id=token,
                room=room,
                permissions=Permissions(
                    user_query=True,
                    user_log_event=True,
                    user_room_join=True,
                    user_room_leave=True,
                    message_text=True,
                    message_image=True,
                    message_command=True,
                    message_broadcast=True,
                    room_query=True,
                    room_log_query=True,
                    room_create=True,
                    room_update=True,
                    room_delete=True,
                    layout_query=True,
                    layout_create=True,
                    layout_update=True,
                    task_create=True,
                    task_query=True,
                    task_update=True,
                    token_generate=True,
                    token_query=True,
                    token_invalidate=True,
                    token_update=True,
                ),
            )
            session.add(token_data)
            session.commit()
            token_id = token_data.id
        return str(token_id)

    @property
    def admin_token(self, default=None):
        with self.create_session() as session:
            tokens = session.query(Token).join(Permissions).filter(
                Permissions.user_query,
                Permissions.user_log_event,
                Permissions.user_room_join,
                Permissions.user_room_leave,
                Permissions.message_text,
                Permissions.message_image,
                Permissions.message_command,
                Permissions.message_broadcast,
                Permissions.room_query,
                Permissions.room_log_query,
                Permissions.room_create,
                Permissions.room_update,
                Permissions.room_delete,
                Permissions.layout_query,
                Permissions.layout_create,
                Permissions.layout_update,
                Permissions.task_create,
                Permissions.task_query,
                Permissions.task_update,
                Permissions.token_generate,
                Permissions.token_query,
                Permissions.token_invalidate,
                Permissions.token_update
            )
            return tokens[0] if tokens.count() > 0 else self.generate_admin_token()

    def init_app(self, app):
        from flask import _app_ctx_stack, current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session

        if not self.engine:
            self.bind(engine=create_engine(current_app.config['DATABASE']))

        app.session = scoped_session(lambda: self.create_session(), scopefunc=_app_ctx_stack.__ident_func__)

        self.init()

        if app.config['DEBUG']:
            admin_token = '00000000-0000-0000-0000-000000000000'
            if not app.session.query(Token).get(admin_token):
                self.generate_admin_token(token=admin_token, api_token=False)
        else:
            admin_token = self.admin_token
        print(f"admin token:\n{admin_token}", flush=True)

        @app.teardown_appcontext
        def cleanup(resp_or_exc):
            if current_app.session.is_active:
                current_app.session.remove()
                getLogger('slurk').debug("Closed database session")
