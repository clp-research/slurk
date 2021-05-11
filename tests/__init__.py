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
def model(engine):
    from app.models import Model

    model = Model(engine=engine)
    yield model

    model.clear()


@pytest.fixture
def admin_token(model):
    return str(model.admin_token)


@pytest.fixture
def app(model):
    return create_app(
        test_config={'TESTING': True, 'SECRET_KEY': os.urandom(16)},
        engine=model.engine
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
                headers.add('Authorization', f'Token {admin_token}')
            kwargs['headers'] = headers
            return super().open(*args, **kwargs)

    app.test_client_class = Client
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
