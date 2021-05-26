import pytest
import docker
import time

from datetime import datetime
from app.openvidu import Connection, OpenViduException, Server, Session


@pytest.fixture(scope='module')
def secret():
    import random
    import string

    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))


@pytest.fixture(scope='module')
def server(secret):
    try:
        client = docker.from_env()
    except Exception as e:
        pytest.skip(f"Could not find docker: {e}")

    try:
        container = client.containers.run('openvidu/openvidu-server-kms:2.17.0',
                                          detach=True,
                                          ports={'4443': 4443},
                                          environment={'OPENVIDU_SECRET': secret})
        yielded = False
        for _ in range(60):
            if b'OpenVidu is ready' in container.logs():
                yield Server('https://localhost:4443', secret, verify=False)
                yielded = True
                break
            time.sleep(1)
        container.stop(timeout=10)
        if not yielded:
            pytest.fail('Could not start OpenVidu Server: Timeout')
    except Exception as e:
        pytest.fail(f"Could not start OpenVidu Server: {e}")
        # pytest.fail(str(e))
    finally:
        client.containers.prune()


@pytest.fixture
def session(server: Server):
    session = server.initialize_session()
    yield session
    session.close()


@pytest.fixture
def connection(session: Session):
    connection = session.create_connection()
    yield connection
    connection.disconnect()


def test_server(server: Server):
    config = server.config
    assert config.pop('version') == '2.17.0'
    assert config.pop('domain_or_public_ip') == 'localhost'
    assert config.pop('https_port') == 4443
    assert config.pop('public_url') == 'https://localhost:4443'
    assert config.pop('cdr') == False

    streams = config.pop('streams')
    video_streams = streams.pop('video')
    assert len(streams) == 0
    assert video_streams.pop('min_send_bandwith')
    assert video_streams.pop('max_send_bandwith')
    assert video_streams.pop('min_recv_bandwith')
    assert video_streams.pop('max_recv_bandwith')

    assert config.pop('recording') is None
    assert config.pop('webhook') is None

    assert len(config) == 0


def test_session_initialization(server: Server):
    assert len(server.sessions) == 0
    session_a = server.initialize_session()
    assert len(server.sessions) == 1
    assert server.sessions[0].id == session_a.id
    session_b = server.initialize_session(custom_session_id=session_a.id)
    assert session_a.id == session_b.id
    assert session_a.custom_session_id is None
    assert session_b.custom_session_id is None
    assert len(server.sessions) == 1
    session_a.close()
    with pytest.raises(OpenViduException):
        session_a.close()
    assert len(server.sessions) == 0

    with pytest.raises(OpenViduException):
        session_c = server.initialize_session(custom_session_id='test session')

    session_d = server.initialize_session(custom_session_id='testsession')
    assert session_d.id == 'testsession'
    assert session_d.custom_session_id == 'testsession'
    session_d.close()
    assert len(server.sessions) == 0


def test_close_unavailable_session(server: Server):
    session = server.initialize_session()
    session.close()
    with pytest.raises(OpenViduException):
        session.close()


def test_session(session: Session):
    assert session.created_at < datetime.now()
    assert session.media_mode == 'ROUTED'
    assert session.recording is False
    assert session.recording_mode == 'MANUAL'
    assert session.default_output_mode == 'COMPOSED'
    assert session.default_recording_layout == 'BEST_FIT'
    assert session.default_custom_layout is None
    assert session.transcoding_allowed is False


def test_connection(connection: Connection):
    assert connection.created_at < datetime.now()
    assert connection.id is not None
    assert connection.type == 'WEBRTC'
    assert connection.role == 'PUBLISHER'
    assert connection.token is not None
