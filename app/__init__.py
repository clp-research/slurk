import sys
import logging
from logging import getLogger

from flask import Flask, request, flash, make_response, jsonify, _app_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session

from .models import Model

logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s')
socketio = SocketIO(ping_interval=5, ping_timeout=120, async_mode="gevent")
login_manager = LoginManager()
model = Model()

def create_app(test_config=None, engine=None):
    app = Flask(__name__)

    if not test_config:
        app.config.from_object('config')
    else:
        app.config.from_mapping(test_config)

    if not engine and 'DATABASE' not in app.config:
        raise ValueError("Database URI not provided. Pass `DATABASE` as environment variable or define it in `config.py`.")
    if 'SECRET_KEY' not in app.config:
        raise ValueError("Secret key not provided. Pass `SECRET_KEY` as environment variable or define it in `config.py`.")

    with app.app_context():
        if engine:
            model.bind(engine)
        model.init_app(app)

        from .api import api as api_blueprint
        from .login import login as login_blueprint
        from .chat import chat as chat_blueprint

        app.register_blueprint(api_blueprint)
        app.register_blueprint(login_blueprint)
        app.register_blueprint(chat_blueprint)

        login_manager.init_app(app)
        login_manager.login_view = 'login.index'

        socketio.init_app(app)


    @app.before_request
    def before_request():
        print("Before request", request.endpoint)
        if request.endpoint and request.endpoint.startswith("api."):
            return

        if not current_user.is_authenticated:
            if request.endpoint != 'login.index' and request.endpoint != "static":
                return login_manager.unauthorized()

    return app



# if not Room.query.get("admin_room"):
#     db.session.add(Room(name="admin_room",
#                         label="Admin Room",
#                         layout=Layout.from_json_file("default"),
#                         static=True))
#     db.session.add(Token(room_name='admin_room',
#                          id='00000000-0000-0000-0000-000000000000' if settings.debug else None,
#                          permissions=Permissions(
#                              user_query=True,
#                              user_log_event=True,
#                              user_room_join=True,
#                              user_room_leave=True,
#                              message_text=True,
#                              message_image=True,
#                              message_command=True,
#                              message_broadcast=True,
#                              room_query=True,
#                              room_log_query=True,
#                              room_create=True,
#                              room_update=True,
#                              room_delete=True,
#                              layout_query=True,
#                              layout_create=True,
#                              layout_update=True,
#                              task_create=True,
#                              task_query=True,
#                              task_update=True,
#                              token_generate=True,
#                              token_query=True,
#                              token_invalidate=True,
#                              token_update=True,
#                          )))
#     db.session.commit()
#     getLogger("slurk").info("generating admin room and token...")
# print("admin token:")
# print(Token.query.order_by(Token.date_created).first().id)
# sys.stdout.flush()
