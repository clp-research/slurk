from functools import wraps
from flask.globals import current_app, g
from flask_httpauth import HTTPTokenAuth as _FlaskHTTPTokenAuth
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import StatementError

from app.extensions.api import abort
from app.models import Token


class HTTPTokenAuth(_FlaskHTTPTokenAuth):
    def login_required(self, func):
        # 'Decorate' the function with the real authentication decorator
        auth_required_func = super().login_required(func)

        # Create the wrapped function.  This just calls the 'decorated' function
        @wraps(func)
        def wrapper(*args, **kwargs):
            return auth_required_func(*args, **kwargs)

        # Update the api docs on the wrapped function and return it to be
        # further decorated by other decorators
        parameters = {
            'name': 'Authorization',
            'in': 'header',
            'description': 'Authorization: Bearer <access_token>',
            'required': 'true'
        }

        wrapper._apidoc = getattr(func, '_apidoc', {})
        wrapper._apidoc.setdefault('parameters', []).append(parameters)

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
