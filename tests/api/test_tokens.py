from .. import *


def test_post(client):
    # Authorization token is overridden, we don't login with a valid token
    response = client.post('/api/v2/token', headers={'Authorization': ''})
    assert response.status_code == 401, response.json['error']

    # Data has to be passed as json
    response = client.post('/api/v2/token', data='invalid json data')
    assert response.status_code == 400, response.json['error']

    # Create a token without any rights
    response = client.post('/api/v2/token')
    assert response.status_code == 200, response.json['error']
    token = response.json

    # Passed a room, which does not exist
    response = client.post('/api/v2/token', json=dict(room='not-a-room'))
    assert response.status_code == 404, response.json['error']

    # Passed a task, which does not exist
    response = client.post('/api/v2/token', json=dict(task=20))
    assert response.status_code == 404, response.json['error']

    # We pass the newly generated token as authorization header. As it is not authorized
    # to create new tokens, we get an error
    response = client.post('/api/v2/token', headers={'Authorization': f'Token {token["id"]}'})
    assert response.status_code == 403, f'Passed "Token {token["id"]}" as authorization'


def test_defaults(client):
    # Create a token without any rights
    token = client.post('/api/v2/token').json

    # Test if the token really has no permissions or a room or a task assigned
    assert token['valid']
    assert not token['room']
    assert not token['task']
    assert not token['permissions']['user']['query']
    assert not token['permissions']['user']['log']['event']
    assert not token['permissions']['user']['room']['join']
    assert not token['permissions']['user']['room']['leave']
    assert not token['permissions']['message']['text']
    assert not token['permissions']['message']['image']
    assert not token['permissions']['message']['command']
    assert not token['permissions']['room']['query']
    assert not token['permissions']['room']['create']
    assert not token['permissions']['room']['update']
    assert not token['permissions']['room']['delete']
    assert not token['permissions']['room']['log']['query']
    assert not token['permissions']['layout']['query']
    assert not token['permissions']['layout']['create']
    assert not token['permissions']['layout']['update']
    assert not token['permissions']['task']['create']
    assert not token['permissions']['task']['query']
    assert not token['permissions']['task']['update']
    assert not token['permissions']['token']['generate']
    assert not token['permissions']['token']['query']
    assert not token['permissions']['token']['invalidate']
    assert not token['permissions']['token']['update']


def test_invalidation(client):
    response = client.post('/api/v2/token')
    assert response.status_code == 200, response.json['error']
    token = response.json

    assert token['valid']

    # Authorization token is overridden, we don't login with a valid token
    response = client.delete(f'/api/v2/token/{token["id"]}', headers={'Authorization': ''})
    assert response.status_code == 401, response.json['error']

    # We pass the newly generated token as authorization header. As it is not authorized
    # to invalidate, we get an error
    response = client.delete(f'/api/v2/token/{token["id"]}', headers={'Authorization': f'Token {token["id"]}'})
    assert response.status_code == 403, f'Passed "Token {token["id"]}" as authorization'

    # Data has to be passed as json
    response = client.delete(f'/api/v2/token/{token["id"]}')
    assert response.status_code == 200, response.json['error']

    response = client.get(f'/api/v2/token/{token["id"]}')
    assert response.status_code == 200, response.json['error']
    token = response.json

    assert not token['valid']


# TODO(TimDiekmann): Create a room and test if it's properly assigned
def test_room(client):
    pass
    # response = client.post('/api/v2/room', json=dict(...))
    # assert response.status_code == 200, response.json['error']
    # room = response.json

    # response = client.post('/api/v2/token', json=dict(room=room.name))
    # assert response.status_code == 200, response.json['error']
    # token = response.json

    # assert room.name == token['room']


# TODO(TimDiekmann): Create a task and test if it's properly assigned
def test_task(client):
    pass
    # response = client.post('/api/v2/task', json=dict(...))
    # assert response.status_code == 200, response.json['error']
    # task = response.json

    # response = client.post('/api/v2/token', json=dict(task=task.id))
    # assert response.status_code == 200, response.json['error']
    # token = response.json

    # assert task.id == token['task']


def test_get(client):
    response = client.post('/api/v2/token')
    assert response.status_code == 200, response.json['error']
    token = response.json

    # Authorization token is overridden, we don't login with a valid token
    response = client.get(f'/api/v2/token/{token["id"]}', headers={'Authorization': ''})
    assert response.status_code == 401, response.json['error']

    # We pass the newly generated token as authorization header. As it is not authorized
    # to invalidate, we get an error
    response = client.get(f'/api/v2/token/{token["id"]}', headers={'Authorization': f'Token {token["id"]}'})
    assert response.status_code == 403, f'Passed "Token {token["id"]}" as authorization'

    # TODO(TimDiekmann): Test different get commands
    pass


def test_gets(client):
    response = client.post('/api/v2/token')
    assert response.status_code == 200, response.json['error']
    token = response.json

    # Authorization token is overridden, we don't login with a valid token
    response = client.get('/api/v2/tokens', headers={'Authorization': ''})
    assert response.status_code == 401, response.json['error']

    # We pass the newly generated token as authorization header. As it is not authorized
    # to invalidate, we get an error
    response = client.get('/api/v2/tokens', headers={'Authorization': f'Token {token["id"]}'})
    assert response.status_code == 403, f'Passed "Token {token["id"]}" as authorization'

    response = client.get('/api/v2/tokens')
    assert response.status_code == 200, response.datajson['error']
    tokens = response.json

    assert token['id'] in tokens


# TODO(TimDiekmann): Test different put commnads
def test_put(client):
    pass
