import pytest
import logging

from app import create_app
from app.extensions.openvidu import OpenVidu


@pytest.fixture(scope='session')
def engine():
    import tempfile
    from sqlalchemy import create_engine

    class NoSQLiteInProduction(logging.Filter):
        def filter(self, record):
            return 'SQLite should not be used in production' not in record.getMessage()

    logging.getLogger('slurk').addFilter(NoSQLiteInProduction())

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


@pytest.fixture(scope='session')
def secret():
    import random
    import string

    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))


@pytest.fixture(scope='session')
def openvidu_impl(secret, request):
    import docker
    import time

    try:
        client = docker.from_env()
        request.addfinalizer(lambda: client.containers.prune())
    except Exception as e:
        yield f'Could not find docker: {e}'
        return

    try:
        container = client.containers.run('openvidu/openvidu-server-kms:2.18.0',
                                          detach=True,
                                          ports={'4443': 4443},
                                          environment={'OPENVIDU_SECRET': secret})
        request.addfinalizer(lambda: container.stop(timeout=10))

        yielded = False
        for _ in range(60):
            if b'OpenVidu is ready' in container.logs():
                yield OpenVidu('https://localhost:4443', secret, verify=False)
                yielded = True
                break
            time.sleep(1)

        if not yielded:
            yield 'Could not start OpenVidu Server: Timeout'
    except Exception as e:
        yield f"Could not start OpenVidu Server: {e}"


@pytest.fixture
def openvidu(openvidu_impl):
    if isinstance(openvidu_impl, str):
        pytest.xfail(openvidu_impl)
    return openvidu_impl


@pytest.fixture
def app(database, openvidu_impl, secret):
    test_config = dict(
        TESTING=True,
        SECRET_KEY=secret,
    )

    if not isinstance(openvidu_impl, str):
        class InsecureConnection(logging.Filter):
            def filter(self, record):
                return 'OPENVIDU_VERIFY' not in record.getMessage()
        logging.getLogger('app').addFilter(InsecureConnection())

        test_config['OPENVIDU_URL'] = 'https://localhost'
        test_config['OPENVIDU_PORT'] = 4443
        test_config['OPENVIDU_SECRET'] = secret
        test_config['OPENVIDU_VERIFY'] = False

    return create_app(test_config=test_config, engine=database.engine)


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
