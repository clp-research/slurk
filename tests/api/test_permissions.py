from http import HTTPStatus
from .. import *


def test_options(client):
    OPTIONS = ['OPTIONS', 'HEAD', 'GET', 'POST']
    response = client.options('/slurk/api/permissions')
    assert response.status_code == HTTPStatus.OK, parse_error(response)
    for option in OPTIONS:
        assert option in response.headers['Allow']


def test_post(client):
    response = client.post('/slurk/api/permissions')
    assert response.status_code == HTTPStatus.CREATED, parse_error(response)
    permissions = response.json

    assert permissions['api'] is False


@pytest.mark.depends(on=["test_get"])
def test_head(client):
    response = client.get('/slurk/api/permissions')
    response = client.head('/slurk/api/permissions',
                           headers={'If-None-Match': response.headers['ETag']})
    assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(on="test_post")
def test_get(client):
    response = client.post('/slurk/api/permissions')
    posted = response.json
    id = posted['id']

    response = client.get('/slurk/api/permissions')
    assert response.status_code == HTTPStatus.OK, parse_error(response)
    token = next(filter(lambda p: p['id'] == id, response.json))
    assert token == posted

    response = client.get('/slurk/api/permissions',
                          headers={'If-None-Match': response.headers['ETag']})
    assert response.status_code == HTTPStatus.NOT_MODIFIED, parse_error(response)


@pytest.mark.depends(on="test_post")
def test_get_id(client):
    response = client.post('/slurk/api/permissions')
    posted = response.json
    id = posted['id']

    response = client.get(f'/slurk/api/permissions/{id}')
    assert response.status_code == HTTPStatus.OK, parse_error(response)
    assert response.json == posted

    response = client.get(f'/slurk/api/permissions/{id}',
                          headers={'If-None-Match': response.headers['ETag']})
    assert response.status_code == HTTPStatus.NOT_MODIFIED, parse_error(response)


@pytest.mark.depends(on="test_post")
def test_head_id(client):
    response = client.post('/slurk/api/permissions')
    response = client.head(f'/slurk/api/permissions/{response.json["id"]}',
                           headers={'If-None-Match': response.headers['ETag']})
    assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(on="test_post")
def test_patch(client):
    response = client.post('/slurk/api/permissions')
    posted = response.json
    id = posted['id']

    response = client.patch(f'/slurk/api/permissions/{id}',
                            headers={'If-Match': response.headers['ETag']},
                            json=dict(api=True))
    assert response.status_code == HTTPStatus.OK, parse_error(response)
    assert posted['api'] is False
    assert response.json['api'] is True
    assert posted['date_modified'] is None
    assert response.json['date_modified'] is not None


@pytest.mark.depends(on="test_post")
def test_put(client):
    response = client.post('/slurk/api/permissions')
    posted = response.json
    id = posted['id']

    response = client.put(f'/slurk/api/permissions/{id}',
                          headers={'If-Match': response.headers['ETag']},
                          json=dict(api=True))
    assert response.status_code == HTTPStatus.OK, parse_error(response)
    assert posted['api'] is False
    assert response.json['api'] is True
    assert posted['date_modified'] is None
    assert response.json['date_modified'] is not None


@pytest.mark.depends(on="test_post")
def test_delete(client):
    response = client.post('/slurk/api/permissions')
    id = response.json['id']

    response = client.delete(f'/slurk/api/permissions/{id}',
                             headers={'If-Match': response.headers['ETag']})
    assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
