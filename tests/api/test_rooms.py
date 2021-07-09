# -*- coding: utf-8 -*-
"""Test requests to the `rooms` table."""

from http import HTTPStatus
import json
import os
from unittest import mock

import pytest

from .. import parse_error
from tests.api import InvalidTemplate, InvalidWithEtagTemplate, RequestOptionsTemplate


PREFIX = f'{__name__.replace(".", os.sep)}.py'


class RoomsTable:
    @property
    def table_name(self):
        return 'rooms'


class TestRequestOptions(RoomsTable, RequestOptionsTemplate):
    @pytest.mark.depends(on=[f'{PREFIX}::TestPostValid'])
    @pytest.mark.parametrize('option', ['PATCH'])
    def test_request_option_with_id_attribute(self, client, option, rooms):
        for attribute_on in {'class', 'id', 'element'}:
            response = client.options(
                f'/slurk/api/rooms/{rooms.json["id"]}/attribute/{attribute_on}/test-field'
            )
            assert response.status_code == HTTPStatus.OK
            assert option in response.headers['Allow'], HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(on=[f'{PREFIX}::TestPostValid'])
    @pytest.mark.parametrize('option', ['POST', 'DELETE'])
    def test_request_option_with_id_class(self, client, option, rooms):
        response = client.options(f'/slurk/api/rooms/{rooms.json["id"]}/class/test-field')
        assert response.status_code == HTTPStatus.OK
        assert option in response.headers['Allow'], HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(on=[f'{PREFIX}::TestPostValid'])
    @pytest.mark.parametrize('option', ['PATCH'])
    def test_request_option_with_id_text(self, client, option, rooms):
        response = client.options(f'/slurk/api/rooms/{rooms.json["id"]}/text/test-field')
        assert response.status_code == HTTPStatus.OK
        assert option in response.headers['Allow'], HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(on=[f'{PREFIX}::TestPostValid'])
    @pytest.mark.parametrize('option', ['GET'])
    def test_request_option_with_id_users(self, client, option, rooms):
        response = client.options(f'/slurk/api/rooms/{rooms.json["id"]}/users')
        assert response.status_code == HTTPStatus.OK
        assert option in response.headers['Allow'], HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(on=[
        f'{PREFIX}::TestPostValid',
        # TODO 'tests/api/test_users.py::TestPostValid'
    ])
    @pytest.mark.parametrize('option', ['GET'])
    def test_request_option_with_id_user_logs(self, client, option, rooms, users):
        response = client.options(
            f'/slurk/api/rooms/{rooms.json["id"]}/users/{users.json["id"]}/logs'
        )
        assert response.status_code == HTTPStatus.OK
        assert option in response.headers['Allow'], HTTPStatus.METHOD_NOT_ALLOWED.description


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option[GET]',
    f'{PREFIX}::TestPostValid'
])
class TestGetValid:
    def test_valid_request(self, client, rooms):
        response = client.get('/slurk/api/rooms')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the posted table instance is included
        def retr_by_id(inst): return inst['id'] == rooms.json['id']
        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == rooms.json

        # check that the `get` request did not alter the database
        response = client.get(
            '/slurk/api/rooms',
            headers={'If-None-Match': response.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option[POST]',
    'tests/api/test_layouts.py::TestPostValid'
])
class TestPostValid:
    REQUEST_CONTENT = [
        {'json': {'layout_id': -1}},
        {'data': {'layout_id': -1}, 'headers': {'Content-Type': 'application/json'}}
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, content, layouts):
        # replace placeholder by valid layout id
        for key in content:
            if content[key].get('layout_id') == -1:
                content[key]['layout_id'] = layouts.json['id']
        data = content.get('json', {}) or content.get('data', {})

        # convert dictionary to json
        if 'data' in content:
            content['data'] = json.dumps(content['data'])

        response = client.post('/slurk/api/rooms', **content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        rooms = response.json
        assert rooms['date_modified'] is None

        assert rooms['layout_id'] == data.get('layout_id')


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option[POST]',
    'tests/api/test_layouts.py::TestPostValid'
])
class TestPostInvalid:
    REQUEST_CONTENT = [
        ({'json': {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'layout_id': -42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': {'layout_id': -1}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, content, status):
        response = client.post('/slurk/api/rooms', **content)
        assert response.status_code == status, parse_error(response)

    @pytest.mark.depends(on=['tests/api/test_tokens.py::TestPostValid'])
    def test_unauthorized_access(self, client, tokens, layouts):
        response = client.post(
            '/slurk/api/rooms',
            json={'layout_id': layouts.json['id']},
            headers={'Authorization': f'Bearer {tokens.json["id"]}'}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client, layouts):
        response = client.post(
            '/slurk/api/rooms',
            json={'layout_id': layouts.json['id']},
            headers={'Authorization': f'Bearer invalid_token'}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]',
    f'{PREFIX}::TestPostValid'
])
class TestGetIdValid:
    def test_valid_request(self, client, rooms):
        response = client.get(f'/slurk/api/rooms/{rooms.json["id"]}')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        assert response.json == rooms.json

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/rooms/{rooms.json["id"]}',
            headers={'If-None-Match': response.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]'
])
class TestGetIdInvalid:
    def test_not_existing(self, client):
        response = client.get('/slurk/api/rooms/invalid_id')
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]',
    f'{PREFIX}::TestPostValid',
    'tests/api/test_layouts.py::TestPostValid'
])
class TestPutValid:
    REQUEST_CONTENT = [
        {'json': {'layout_id': -1}}
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, rooms, content):
        # replace placeholder by valid layout id different from layout fixture id
        for key in content:
            if content[key].get('layout_id') == -1:
                # cannot be fixture layouts because this was already used in post
                layouts = client.post('/slurk/api/layouts', json={'title': 'Test Room'})
                content[key]['layout_id'] = layouts.json['id']
        data = content.get('json', {}) or content.get('data', {})

        # set the etag
        content.setdefault('headers', {}).update({'If-Match': rooms.headers['ETag']})

        response = client.put(f'/slurk/api/rooms/{rooms.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_rooms = response.json

        # check that a modification was performed without creating new table entry
        assert new_rooms['id'] == rooms.json['id']
        assert new_rooms['date_created'] == rooms.json['date_created']
        assert response.json['date_modified'] is not None
        assert response.headers['ETag'] != rooms.headers['ETag']

        assert new_rooms['layout_id'] == data.get('layout_id')


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]',
    f'{PREFIX}::TestPostValid',
    'tests/api/test_layouts.py::TestPostValid'
])
class TestPutInvalid(RoomsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'put'

    def json(self, request):
        layouts = request.getfixturevalue('layouts')
        return {'json': {'layout_id': layouts.json['id']}}

    REQUEST_CONTENT = [
        ({'json': {'id': 2}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': '{"layout_id": -1}'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, rooms, content, status):
        # set the etag
        content.setdefault('headers', {}).update({'If-Match': rooms.headers['ETag']})

        response = client.put(f'/slurk/api/rooms/{rooms.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]',
    f'{PREFIX}::TestPostValid'
])
class TestDeleteValid:
    def test_valid_request(self, client, rooms):
        response = client.delete(
            f'/slurk/api/rooms/{rooms.json["id"]}',
            headers={'If-Match': rooms.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]',
    f'{PREFIX}::TestPostValid'
])
class TestDeleteInvalid(RoomsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'delete'

    @pytest.mark.depends(on=[
        'tests/api/test_tokens.py::TestPostValid',
        'tests/api/test_tokens.py::TestDeleteValid',
        'tests/api/test_permissions.py::TestPostValid'
    ])
    def test_deletion_of_room_in_token(self, client, rooms, permissions):
        # create token that uses the room
        token = client.post(
            '/slurk/api/tokens',
            json={'permissions_id': permissions.json['id'], 'room_id': rooms.json['id']}
        )
        # the deletion of a room entry that is in use should fail
        response = client.delete(
            f'/slurk/api/rooms/{rooms.json["id"]}',
            headers={'If-Match': rooms.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(response)

        # free the rooms entry by deleting the token
        client.delete(
            f'/slurk/api/tokens/{token.json["id"]}',
            headers={'If-Match': token.headers['ETag']}
        )
        # now one should be able to delete the rooms
        response = client.delete(
            f'/slurk/api/rooms/{rooms.json["id"]}',
            headers={'If-Match': rooms.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)

    @pytest.mark.depends(on=[
        # TODO 'tests/api/test_logs.py::TestPostValid',
        # TODO 'tests/api/test_logs.py::TestDeleteValid'
    ])
    def test_deletion_of_room_in_logs(self, client, rooms):
        # create logs that use the room
        log = client.post(
            '/slurk/api/logs',
            json={'event': 'Test Event', 'room_id': rooms.json['id']}
        )
        # the deletion of a room entry that is in use should fail
        response = client.delete(
            f'/slurk/api/rooms/{rooms.json["id"]}',
            headers={'If-Match': rooms.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)

        # Check if the log entry is deleted
        response = client.get(f'/slurk/api/logs/{log.json["id"]}')
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]',
    f'{PREFIX}::TestPostValid',
    'tests/api/test_layouts.py::TestPostValid'
])
class TestPatchValid:
    REQUEST_CONTENT = [
        {'json': {'layout_id': -1}},
        {'data': {'layout_id': -1}, 'headers': {'Content-Type': 'application/json'}}
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, rooms, content):
        data = content.get('json', {}) or content.get('data', {})
        # replace placeholder by valid layout id different from layout fixture id
        for key in content:
            if content[key].get('layout_id') == -1:
                # cannot be fixture layouts because this was already used in post
                layouts = client.post('/slurk/api/layouts', json={'title': 'Test Room'})
                content[key]['layout_id'] = layouts.json['id']

        # convert dictionary to json
        if 'data' in content:
            content['data'] = json.dumps(content['data'])

        # set the etag
        content.setdefault('headers', {}).update({'If-Match': rooms.headers['ETag']})

        response = client.patch(f'/slurk/api/rooms/{rooms.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_rooms = response.json

        # check that a modification was performed without creating new table entry
        assert new_rooms['id'] == rooms.json['id']
        assert new_rooms['date_created'] == rooms.json['date_created']
        assert response.json['date_modified'] is not None
        assert response.headers['ETag'] != rooms.headers['ETag']

        expected_send_command = data.get('layout_id', rooms.json['layout_id'])
        assert new_rooms['layout_id'] == expected_send_command


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]',
    f'{PREFIX}::TestPostValid',
    'tests/api/test_layouts.py::TestPostValid'
])
class TestPatchInvalid(RoomsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'patch'

    REQUEST_CONTENT = [
        ({'json': {'layout_id': -42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'date_modified': 'something'}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': {'layout_id': -1}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, rooms, content, status):
        # replace placeholder by valid layout id different from layout fixture id
        for key in content:
            if content[key].get('layout_id') == -1:
                # cannot be fixture layouts because this was already used in post
                layouts = client.post(f'/slurk/api/layouts', json={'title': 'Test Room'})
                content[key]['layout_id'] = layouts.json['id']
        # set the etag
        content.setdefault('headers', {}).update({'If-Match': rooms.headers['ETag']})

        response = client.patch(f'/slurk/api/rooms/{rooms.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_attribute[PATCH]',
    f'{PREFIX}::TestPostValid'
])
class TestPatchAttributeValid:
    REQUEST_CONTENT = [
        ({'json': {'attribute': 'color', 'value': 'red'}}, 'id'),
        ({'json': {'attribute': 'background-color', 'value': 'yellow'}}, 'class'),
        ({'json': {'attribute': 'font-size', 'value': '30px'}}, 'element')
    ]

    @pytest.mark.parametrize('content, attribute_on', REQUEST_CONTENT)
    def test_valid_request(self, client, rooms, content, attribute_on):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get('json', {}) or content.get('data', {})

            # test-field could here be a custom class, id or a pseudo element
            response = client.patch(
                f'/slurk/api/rooms/{rooms.json["id"]}/attribute/{attribute_on}/test-field',
                **content
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            # check that event was triggered
            socketio_mock.assert_called_with(
                'attribute_update',
                {**data, 'cls' if attribute_on == 'class' else attribute_on: 'test-field'},
                room=str(rooms.json['id'])
            )


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_attribute[PATCH]',
    f'{PREFIX}::TestPostValid'
])
class TestPatchAttributeInvalid(RoomsTable, InvalidTemplate):
    @property
    def request_method(self):
        return 'patch'

    @property
    def url_extension(self):
        # test for only one of the three objects one can alter features on
        return '/attribute/id/test-field'

    def json(self, request):
        return {'json': {'attribute': 'color', 'value': 'red'}}

    REQUEST_CONTENT = [
        (
            {'json': {'other': 'test'}}, 'id',
            HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
            {'json': {'attribute': 'font-size', 'value': 30}}, 'id',
            HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
            {'json': {'attribute': None, 'value': 'yellow'}}, 'class',
            HTTPStatus.UNPROCESSABLE_ENTITY
        ),
        (
            {'data': {'attribute': 'color', 'value': 'red'}}, 'element',
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE
        )
    ]

    @pytest.mark.parametrize('content, attribute_on, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, rooms, content, attribute_on, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.patch(
                f'/slurk/api/rooms/{rooms.json["id"]}/attribute/{attribute_on}/test-field',
                **content
            )
            assert response.status_code == status, parse_error(response)
            # check that event was not triggered
            socketio_mock.assert_not_called()


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_class[POST]',
    f'{PREFIX}::TestPostValid'
])
class TestPostClassValid:
    REQUEST_CONTENT = [
        {'json': {'class': 'test'}},
        {'data': {'class': 'test'}, 'headers': {'Content-Type': 'application/json'}}
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, rooms, content):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get('json', {}) or content.get('data', {})

            # convert dictionary to json
            if 'data' in content:
                content['data'] = json.dumps(content['data'])

            response = client.post(
                f'/slurk/api/rooms/{rooms.json["id"]}/class/test-field',
                **content
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            # check that event was triggered
            socketio_mock.assert_called_with(
                'class_add',
                {**data, 'id': 'test-field'},
                room=str(rooms.json['id'])
            )


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_class[POST]',
    f'{PREFIX}::TestPostValid'
])
class TestPostClassInvalid(RoomsTable, InvalidTemplate):
    @property
    def request_method(self):
        return 'post'

    @property
    def url_extension(self):
        return '/class/test-field'

    def json(self, request):
        return {'json': {'class': 'test'}}

    REQUEST_CONTENT = [
        ({'json': {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'class': 24}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': {'class': 'test'}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, rooms, content, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.post(
                f'/slurk/api/rooms/{rooms.json["id"]}/class/test-field',
                **content
            )
            assert response.status_code == status, parse_error(response)
            # check that event was not triggered
            socketio_mock.assert_not_called()


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_class[DELETE]',
    f'{PREFIX}::TestPostValid'
])
class TestDeleteClassValid:
    REQUEST_CONTENT = [
        {'json': {'class': 'test'}},
        {'data': {'class': 'test'}, 'headers': {'Content-Type': 'application/json'}}
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, rooms, content):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get('json', {}) or content.get('data', {})

            # convert dictionary to json
            if 'data' in content:
                content['data'] = json.dumps(content['data'])

            response = client.delete(
                f'/slurk/api/rooms/{rooms.json["id"]}/class/test-field',
                **content
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            # check that event was triggered
            socketio_mock.assert_called_with(
                'class_remove',
                {**data, 'id': 'test-field'},
                room=str(rooms.json['id'])
            )


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_class[DELETE]',
    f'{PREFIX}::TestPostValid'
])
class TestDeleteClassInvalid(RoomsTable, InvalidTemplate):
    @property
    def request_method(self):
        return 'delete'

    @property
    def url_extension(self):
        return '/class/test-field'

    def json(self, request):
        return {'json': {'class': 'test'}}

    REQUEST_CONTENT = [
        ({'json': {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'class': None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': {'class': 'test'}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, rooms, content, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.delete(
                f'/slurk/api/rooms/{rooms.json["id"]}/class/test-field',
                **content
            )
            assert response.status_code == status, parse_error(response)
            # check that event was not triggered
            socketio_mock.assert_not_called()


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_text[PATCH]',
    f'{PREFIX}::TestPostValid'
])
class TestPatchTextValid:
    REQUEST_CONTENT = [
        {'json': {'text': 'test'}}
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, rooms, content):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get('json', {}) or content.get('data', {})

            response = client.patch(
                f'/slurk/api/rooms/{rooms.json["id"]}/text/test-field',
                **content
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            # check that event was triggered
            socketio_mock.assert_called_with(
                'text_update',
                {**data, 'id': 'test-field'},
                room=str(rooms.json['id'])
            )


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_text[PATCH]',
    f'{PREFIX}::TestPostValid'
])
class TestPatchTextInvalid(RoomsTable, InvalidTemplate):
    @property
    def request_method(self):
        return 'patch'

    @property
    def url_extension(self):
        return '/text/test-field'

    def json(self, request):
        return {'json': {'text': 'test'}}

    REQUEST_CONTENT = [
        ({'json': {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'text': None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'class': 'div'}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': {'text': 'test'}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, rooms, content, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.patch(
                f'/slurk/api/rooms/{rooms.json["id"]}/text/test-field',
                **content
            )
            assert response.status_code == status, parse_error(response)
            socketio_mock.assert_not_called()


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_users[GET]',
    f'{PREFIX}::TestPostValid'
])
class TestGetUsersByRoomByIdValid:
    def test_valid_request(self, client, rooms):
        response = client.get(f'/slurk/api/rooms/{rooms.json["id"]}/users')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # during a test run no user is actively logged in
        assert response.json == []

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/rooms/{rooms.json["id"]}/users',
            headers={'If-None-Match': response.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(on=[
    f'{PREFIX}::TestRequestOptions::test_request_option_with_id_user_logs[GET]',
    f'{PREFIX}::TestPostValid',
    # TODO 'tests/api/test_users.py::TestPostValid',
    # TODO 'tests/api/test_logs.py::TestPostValid'
])
class TestGetLogsByUserByRoomByIdValid:
    def test_valid_request(self, client, rooms, users, logs):
        response = client.get(f'/slurk/api/rooms/{rooms.json["id"]}/users/{users.json["id"]}/logs')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # atleast the logs fixture entry should be included
        def retr_by_id(inst): return inst['id'] == logs.json['id']
        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == logs.json

        # all logs should have the specified room
        assert all(map(lambda log: log['room_id'] == rooms.json['id'], response.json))

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/rooms/{rooms.json["id"]}/users/{users.json["id"]}/logs',
            headers={'If-None-Match': response.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED
