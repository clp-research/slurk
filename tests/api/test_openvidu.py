import pytest
import docker
import time

from http import HTTPStatus

from slurk.extensions.openvidu import OpenVidu

from tests import parse_error


@pytest.mark.usefixtures('openvidu')
def test_server(client):
    response = client.get('/slurk/api/openvidu/config')
    assert response.status_code == HTTPStatus.OK, parse_error(response)
    config = response.json

    assert config['version'] == '2.18.0'
    assert config['domain_or_public_ip'] == 'localhost'
    assert config['https_port'] == 4443
    assert config['public_url'] == 'https://localhost:4443'
