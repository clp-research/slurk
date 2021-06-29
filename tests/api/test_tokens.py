import pytest

from http import HTTPStatus

from tests import parse_error


@pytest.fixture
def permissions_id(client):
    return client.post('/slurk/api/permissions').json['id']


def test_options(client):
    OPTIONS = ['OPTIONS', 'HEAD', 'GET', 'POST']
    response = client.options('/slurk/api/tokens')
    assert response.status_code == HTTPStatus.OK, parse_error(response)
    for option in OPTIONS:
        assert option in response.headers['Allow']


@pytest.mark.depends(on=["tests/api/test_permissions.py::test_post"])
def test_post(client, permissions_id):
    response = client.post('/slurk/api/tokens', json=dict(permissions_id=permissions_id))
    assert response.status_code == HTTPStatus.CREATED, parse_error(response)
    permissions = response.json
