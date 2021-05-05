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

    class TestClient(testing.FlaskClient):
        def open(self, *args, **kwargs):
            headers = kwargs.pop('headers', Headers())
            if isinstance(headers, dict):
                headers = Headers(headers)
            headers.add('Authorization', f'Token {admin_token}')
            kwargs['headers'] = headers
            return super().open(*args, **kwargs)

    app.test_client_class = TestClient
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def environment():
    old_environ = dict(os.environ)
    os.environ.clear()
    database_file = tempfile.NamedTemporaryFile()
    os.environ.update({
        'SECRET_KEY': 'test',
        'DATABASE': f'sqlite:///{database_file.name}.db'
    })

    yield

    os.environ.clear()
    os.environ.update(old_environ)


# @pytest.fixture
# def token(app):
#     from app.models import Token, Permissions, Room, Layout

#     db = app.session
#     print(db.query(Layout).all())
#     token = Token(
#         id='00000000-0000-0000-0000-000000000000',
#         permissions=Permissions(
#             token_query=True,
#         ),
#         room=Room(
#             name="test_room",
#             label="Test Room",
#             layout=Layout.from_json_file("default"),
#             static=True))
#     db.add(token)
#     db.commit()
