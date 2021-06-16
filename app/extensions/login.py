from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask.globals import request
from flask_login import LoginManager, current_user

login_manager = LoginManager()


def init_app(app):
    login_manager.login_view = 'login.index'
    login_manager.init_app(app)
