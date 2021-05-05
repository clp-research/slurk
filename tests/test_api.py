import json

from . import *
from app.models import Token

from logging import getLogger


def test_tokens(client, app):
    # TODO(TimDiekmann): Add tests for different permissions
    rv = client.post('/api/v2/token', json=dict(room=None))
    custom_token = rv.get_json()

    rv = client.get('/api/v2/tokens')
    json_data = rv.get_json()

    assert str(custom_token) in json_data


def test_get_token(client, app):
    rv = client.post('/api/v2/token', json=dict(room=None))
    custom_token = rv.get_json()

    rv = client.get(f'/api/v2/token/{custom_token}')
    retreived_token = rv.get_json()

    assert retreived_token['id'] == custom_token
    assert not retreived_token['room']
