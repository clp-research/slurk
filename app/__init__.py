import sys
import logging
from logging import getLogger

from flask import Flask, request, flash, make_response, jsonify
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

from .api import api as api_blueprint
from .login import login as login_blueprint
from .chat import chat as chat_blueprint

app.register_blueprint(api_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(chat_blueprint)

from .models.room import Room
from .models.token import Token
from .models.layout import Layout
from .models.permission import Permissions
from .models.task import Task
from .models.log import Log

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
    if request.endpoint and request.endpoint.startswith("api."):
        return

    if not current_user.is_authenticated:
        if request.endpoint != 'login.index' and request.endpoint != "static":
            return login_manager.unauthorized()

    if request.endpoint == 'admin.token' and not current_user.token.permissions.token_generate \
            or request.endpoint == 'admin.task' and not current_user.token.permissions.task_create:
        flash("Permission denied", "error")
        return login_manager.unauthorized()


if not Room.query.get("admin_room"):
    db.session.add(Room(name="admin_room",
                        label="Admin Room",
                        layout=Layout.from_json_file("default"),
                        static=True))
    db.session.add(Token(room_name='admin_room',
                         id='00000000-0000-0000-0000-000000000000' if settings.debug else None,
                         permissions=Permissions(
                             user_query=True,
                             user_log_query=True,
                             user_log_event=True,
                             user_permissions_query=True,
                             user_permissions_update=True,
                             user_room_query=True,
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
                             room_close=True,
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
                         )))
    db.session.commit()
    getLogger("slurk").info("generating admin room and token...")
print("admin token:")
print(Token.query.order_by(Token.date_created).first().id)
sys.stdout.flush()
