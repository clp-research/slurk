from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

import configparser

socketio = SocketIO(ping_interval=5, ping_timeout=120, async_mode="gevent")


login_manager = LoginManager()

config = None


def create_app(debug=False):
    global config

    config = configparser.ConfigParser()
    config.read("config.ini")

    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = config['server']['secret-key']

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)
    login_manager.init_app(app)
    return app


@login_manager.user_loader
def load_user(user_id):
    from .main.User import User
    return User.from_id(user_id)
