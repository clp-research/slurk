import sys
import logging
from logging import getLogger

from flask import Flask, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO

from sqlalchemy import event
from sqlalchemy.engine import Engine

from .settings import Settings

logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s')

socketio = SocketIO(ping_interval=5, ping_timeout=120, async_mode="gevent")

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
settings = Settings.from_object('config')
login_manager = LoginManager()

from .login import login as login_blueprint
from .admin import admin as admin_blueprint
from .chat import chat as chat_blueprint

app.register_blueprint(login_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(chat_blueprint)

if settings.drop_database_on_startup:
    db.drop_all()
db.create_all()
login_manager.init_app(app)
login_manager.login_view = 'login.index'
socketio.init_app(app)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    if settings.database_url.startswith('sqlite://'):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@app.before_request
def before_request():
    if not current_user.is_authenticated and request.endpoint != 'login.index' and request.endpoint != "static":
        return login_manager.unauthorized()

    if request.endpoint == 'admin.token' and not current_user.token.permissions.token_generate \
            or request.endpoint == 'admin.task' and not current_user.token.permissions.task_create:
        flash("Permission denied", "error")
        return login_manager.unauthorized()


from .models.room import Room
from .models.token import Token
from .models.layout import Layout
from .models.permission import Permissions
from .models.task import Task

if not Room.query.get("test_room"):
    meetup = Task(name="Meetup", num_users=2)
    admin_token = Token(room_name='test_room',
                        id='00000000-0000-0000-0000-000000000000' if settings.debug else None,
                        task=meetup,
                        permissions=Permissions(
                            user_query=True,
                            user_permissions_query=True,
                            user_permissions_update=True,
                            user_room_query=True,
                            user_room_join=True,
                            user_room_leave=True,
                            message_text=True,
                            message_image=True,
                            message_command=True,
                            message_history=True,
                            message_broadcast=True,
                            room_query=True,
                            room_create=True,
                            room_close=True,
                            layout_query=True,
                            task_create=True,
                            task_query=True,
                            token_generate=True,
                            token_query=True,
                            token_invalidate=True,
                            token_remove=True,
                        ))
    db.session.add(admin_token)
    db.session.add(Token(room_name='test_room',
                         id='00000000-0000-0000-0000-000000000001' if settings.debug else None,
                         permissions=Permissions(
                             user_query=True,
                             user_permissions_query=True,
                             user_permissions_update=True,
                             user_room_query=True,
                             user_room_join=True,
                             user_room_leave=True,
                             message_text=True,
                             message_image=True,
                             message_command=True,
                             message_history=True,
                             message_broadcast=True,
                             room_query=True,
                             room_create=True,
                             room_close=True,
                             task_create=True,
                             task_query=True,
                             layout_query=True,
                             token_generate=True,
                             token_query=True,
                             token_invalidate=True,
                             token_remove=True,
                         )))
    db.session.add(Room(name="test_room",
                        label="Test Room",
                        static=True,
                        layout=Layout.from_json_file("test_room")))
    db.session.commit()
    getLogger("slurk").info("generating test room and admin token...")
print("admin token:")
print(Token.query.order_by(Token.date_created).first().id)
sys.stdout.flush()
