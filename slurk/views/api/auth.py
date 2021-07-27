from functools import wraps
from flask.globals import current_app
from flask_httpauth import HTTPTokenAuth as _FlaskHTTPTokenAuth
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import StatementError

from slurk.extensions.api import abort
from slurk.models import Token


class HTTPTokenAuth(_FlaskHTTPTokenAuth):
    def login_required(self, func):
        # 'Decorate' the function with the real authentication decorator
        auth_required_func = super().login_required(func)

        # Create the wrapped function.  This just calls the 'decorated' function
        @wraps(func)
        def wrapper(*args, **kwargs):
            return auth_required_func(*args, **kwargs)

        return wrapper


auth = HTTPTokenAuth()


@auth.error_handler
def unauthorized():
    abort(Unauthorized)


@auth.verify_token
def verify_token(token):
    db = current_app.session
    try:
        token = db.query(Token).get(token)
    except StatementError:
        abort(Unauthorized)
    return token and token.permissions.api
