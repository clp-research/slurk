from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask.globals import request
from flask_login import LoginManager, current_user

login_manager = LoginManager()


def init_app(app):
    login_manager.login_view = 'login.index'
    login_manager.init_app(app)

    @app.before_request
    def before_request():
        ALLOWED_ENDPOINTS = [
            'api',
            'static',
            'api-docs',
            'login',
        ]
        return

        if request.endpoint:
            for allowed in ALLOWED_ENDPOINTS:
                if request.endpoint.startswith(allowed):
                    return

        if not current_user.is_authenticated:
            return login_manager.unauthorized()
