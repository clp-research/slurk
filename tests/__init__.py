import os
import tempfile

import pytest

from app import create_app


@pytest.fixture(scope='session')
def engine():
    from sqlalchemy import create_engine

    with tempfile.NamedTemporaryFile() as f:
        yield create_engine(f'sqlite:///{f.name}')


@pytest.fixture
def database(engine):
    from app.extensions.database import Database

    database = Database(engine=engine)
    yield database

    database.clear()


@pytest.fixture
def admin_token(database):
    from app.models import Token

    return str(Token.get_admin_token(database))


@pytest.fixture
def app(database):
    return create_app(
        test_config={'TESTING': True, 'SECRET_KEY': os.urandom(16)},
        engine=database.engine
    )


@pytest.fixture
def client(app, admin_token):
    from flask import testing
    from werkzeug.datastructures import Headers

    class Client(testing.FlaskClient):
        def open(self, *args, **kwargs):
            headers = kwargs.pop('headers', Headers())
            if isinstance(headers, dict):
                headers = Headers(headers)
            if 'Authorization' not in headers:
                headers.add('Authorization', f'bearer {admin_token}')
            kwargs['headers'] = headers
            return super().open(*args, **kwargs)

    app.test_client_class = Client
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def parse_error(response):
    if 'errors' in response.json:
        return response.json['errors']
    else:
        return response.json.get('message', 'Unknown Error')
