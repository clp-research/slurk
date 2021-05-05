from logging import getLogger

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

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
        getLogger('slurk').debug("Creating new database session")
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
        room = Room(name='admin_room',
                    label='Admin Room',
                    layout=Layout.from_json_file('default')) if not api_token else None
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
                    Permissions.user_query==True,
                    Permissions.user_log_event==True,
                    Permissions.user_room_join==True,
                    Permissions.user_room_leave==True,
                    Permissions.message_text==True,
                    Permissions.message_image==True,
                    Permissions.message_command==True,
                    Permissions.message_broadcast==True,
                    Permissions.room_query==True,
                    Permissions.room_log_query==True,
                    Permissions.room_create==True,
                    Permissions.room_update==True,
                    Permissions.room_delete==True,
                    Permissions.layout_query==True,
                    Permissions.layout_create==True,
                    Permissions.layout_update==True,
                    Permissions.task_create==True,
                    Permissions.task_query==True,
                    Permissions.task_update==True,
                    Permissions.token_generate==True,
                    Permissions.token_query==True,
                    Permissions.token_invalidate==True,
                    Permissions.token_update==True
                )
            if tokens.count() == 0:
                return self.generate_admin_token(api_token=False)
            else:
                return tokens[0]


    def init_app(self, app):
        from flask import _app_ctx_stack, current_app
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session

        with app.app_context():
            @app.teardown_appcontext
            def cleanup(resp_or_exc):
                if current_app.session:
                    getLogger('slurk').debug("Closing session")
                    current_app.session.remove()
                else:
                    getLogger('slurk').debug("Attempting to close session but none exist")

            if not self.engine:
                self.bind(engine=create_engine(current_app.config['DATABASE']))

            app.session = scoped_session(
                lambda: self.create_session(), scopefunc=_app_ctx_stack.__ident_func__)

            self.init()

            if current_app.config['DEBUG']:
                admin_token = '00000000-0000-0000-0000-000000000000'
                with self.create_session() as session:
                    if not session.query(Token).get(admin_token):
                        self.generate_admin_token(token=admin_token, api_token=False)
            else:
                admin_token = self.admin_token
            getLogger('slurk').info(f'Admin token: {admin_token}')
