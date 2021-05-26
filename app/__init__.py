from app.models.openvidu import OpenViduSession
import sys
import logging
from logging import getLogger

from flask import Flask, request, flash, make_response, jsonify, _app_ctx_stack
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session

from .models import Model
from . import openvidu

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

        if 'OPENVIDU_URL' in app.config:
            openvidu_url = app.config['OPENVIDU_URL']
            openvidu_port = app.config['OPENVIDU_PORT']
            openvidu_secret = app.config.get('OPENVIDU_SECRET')
            openvidu_verify = app.config.get('OPENVIDU_VERIFY', True)
            if not openvidu_secret:
                raise ValueError(
                    "OpenVidu Secret key not provided. Pass `OPENVIDU_SECRET_KEY` as environment variable or define it in `config.py`.")

            getLogger('slurk').info(f"Initializing OpenVidu connection to \"{openvidu_url}:{openvidu_port}\"")
            if not openvidu_verify:
                getLogger('slurk').warning(
                    "OpenVidu connection may be unsecure. Set `OPENVIDU_VERIFY` to true or don't pass this variable")
            app.openvidu = openvidu.Server(f'{openvidu_url}:{openvidu_port}', openvidu_secret, verify=openvidu_verify)

            with model.create_session() as db:
                for openvidu_session in db.query(OpenViduSession).all():
                    getLogger('slurk').warning(openvidu_session.as_dict())

    @app.before_request
    def before_request():
        if request.endpoint and request.endpoint.startswith("api."):
            return

        if not current_user.is_authenticated:
            if request.endpoint != 'login.index' and request.endpoint != "static":
                return login_manager.unauthorized()

    return app
