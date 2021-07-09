# -*- coding: utf-8 -*-
"""Test requests to the `permissions` table."""

from http import HTTPStatus
import json
import os

import pytest

from .. import parse_error
from tests.api import InvalidWithEtagTemplate, RequestOptionsTemplate


PREFIX = f'{__name__.replace(".", os.sep)}.py'


class PermissionsTable:
    @property
    def table_name(self):
        return 'permissions'


class TestRequestOptions(PermissionsTable, RequestOptionsTemplate):
    pass


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option[GET]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestGetValid:
    def test_valid_request(self, client, permissions):
        response = client.get('/slurk/api/permissions')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the posted table instance is included
        def retr_by_id(inst):
            return inst['id'] == permissions.json['id']

        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == permissions.json

        # check that the `get` request did not alter the database
        response = client.get(
            '/slurk/api/permissions',
            headers={'If-None-Match': response.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(on=[f'{PREFIX}::TestRequestOptions::test_request_option[POST]'])
class TestPostValid:
    REQUEST_CONTENT = [
        {},
        {'json': {}},
        {
            'json': {
                'api': False,
                'send_message': True,
                'send_image': False,
                'send_command': True,
            }
        },
        {'data': {'api': True}, 'headers': {'Content-Type': 'application/json'}},
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, content):
        data = content.get('json', {}) or content.get('data', {})
        # convert dictionary to json
        if 'data' in content:
            content['data'] = json.dumps(content['data'])

        response = client.post('/slurk/api/permissions', **content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        permissions = response.json
        assert permissions['date_modified'] is None

        assert permissions['api'] == data.get('api', False)
        assert permissions['send_message'] == data.get('send_message', False)
        assert permissions['send_image'] == data.get('send_image', False)
        assert permissions['send_command'] == data.get('send_command', False)


@pytest.mark.depends(on=[f'{PREFIX}::TestRequestOptions::test_request_option[POST]'])
class TestPostInvalid:
    REQUEST_CONTENT = [
        ({'json': {'send_image': None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'api': 'not_a_boolean'}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'not_existing': True}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': 'not_a_dict'}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': '{"api": true}'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, content, status):
        response = client.post('/slurk/api/permissions', **content)
        assert response.status_code == status, parse_error(response)

    @pytest.mark.depends(on=['tests/api/test_tokens.py::TestPostValid'])
    def test_unauthorized_access(self, client, tokens):
        response = client.post(
            '/slurk/api/permissions',
            headers={'Authorization': f'Bearer {tokens.json["id"]}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client):
        response = client.post(
            '/slurk/api/permissions', headers={'Authorization': 'Bearer invalid_token'}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestGetIdValid:
    def test_valid_request(self, client, permissions):
        response = client.get(f'/slurk/api/permissions/{permissions.json["id"]}')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        assert response.json == permissions.json

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/permissions/{permissions.json["id"]}',
            headers={'If-None-Match': response.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[f'{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]']
)
class TestGetIdInvalid:
    def test_not_existing(self, client):
        response = client.get('/slurk/api/permissions/invalid_id')
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestPutValid:
    REQUEST_CONTENT = [
        {'json': {'api': False, 'send_message': False}},
        {'json': {'send_message': False, 'send_image': True}},
        {
            'data': {'send_command': True},
            'headers': {'Content-Type': 'application/json'},
        },
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, permissions, content):
        data = content.get('json', {}) or content.get('data', {})
        # convert dictionary to json
        if 'data' in content:
            content['data'] = json.dumps(content['data'])

        # set the etag
        content.setdefault('headers', {}).update(
            {'If-Match': permissions.headers['ETag']}
        )

        response = client.put(
            f'/slurk/api/permissions/{permissions.json["id"]}', **content
        )
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_permissions = response.json

        # check that a modification was performed without creating new table entry
        assert new_permissions['id'] == permissions.json['id']
        assert new_permissions['date_created'] == permissions.json['date_created']
        assert response.json['date_modified'] is not None
        assert response.headers['ETag'] != permissions.headers['ETag']

        assert new_permissions['api'] == data.get('api', False)
        assert new_permissions['send_message'] == data.get('send_message', False)
        assert new_permissions['send_image'] == data.get('send_image', False)
        assert new_permissions['send_command'] == data.get('send_command', False)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestPutInvalid(PermissionsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'put'

    REQUEST_CONTENT = [
        ({'json': {'send_command': 42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'api': None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'id': 42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': '{}'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, permissions, content, status):
        # set the etag
        content.setdefault('headers', {}).update(
            {'If-Match': permissions.headers['ETag']}
        )

        response = client.put(
            f'/slurk/api/permissions/{permissions.json["id"]}', **content
        )
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestDeleteValid:
    def test_valid_request(self, client, permissions):
        response = client.delete(
            f'/slurk/api/permissions/{permissions.json["id"]}',
            headers={'If-Match': permissions.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestDeleteInvalid(PermissionsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'delete'

    @pytest.mark.depends(
        on=[
            'tests/api/test_tokens.py::TestPostValid',
            'tests/api/test_tokens.py::TestDeleteValid',
        ]
    )
    def test_deletion_of_permission_in_token(self, client, permissions):
        # create token that uses the permissions
        token = client.post(
            '/slurk/api/tokens', json={'permissions_id': permissions.json['id']}
        )
        # the deletion of a permissions entry that is in use should fail
        response = client.delete(
            f'/slurk/api/permissions/{permissions.json["id"]}',
            headers={'If-Match': permissions.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
            response
        )

        # free the permissions entry by deleting the token
        client.delete(
            f'/slurk/api/tokens/{token.json["id"]}',
            headers={'If-Match': token.headers['ETag']},
        )
        # now one should be able to delete the permissions
        response = client.delete(
            f'/slurk/api/permissions/{permissions.json["id"]}',
            headers={'If-Match': permissions.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestPatchValid:
    REQUEST_CONTENT = [
        {'json': {'send_command': True}},
        {'json': {'api': False, 'send_image': True}},
        {'data': {'api': True}, 'headers': {'Content-Type': 'application/json'}},
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, permissions, content):
        data = content.get('json', {}) or content.get('data', {})
        # convert dictionary to json
        if 'data' in content:
            content['data'] = json.dumps(content['data'])

        # set the etag
        content.setdefault('headers', {}).update(
            {'If-Match': permissions.headers['ETag']}
        )

        response = client.patch(
            f'/slurk/api/permissions/{permissions.json["id"]}', **content
        )
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_permissions = response.json

        # check that a modification was performed without creating new table entry
        assert new_permissions['id'] == permissions.json['id']
        assert new_permissions['date_created'] == permissions.json['date_created']
        assert response.json['date_modified'] is not None
        assert response.headers['ETag'] != permissions.headers['ETag']

        expected_api = data.get('api', permissions.json['api'])
        assert new_permissions['api'] == expected_api
        expected_send_message = data.get(
            'send_message', permissions.json['send_message']
        )
        assert new_permissions['send_message'] == expected_send_message
        expected_send_image = data.get('send_image', permissions.json['send_image'])
        assert new_permissions['send_image'] == expected_send_image
        expected_send_command = data.get(
            'send_command', permissions.json['send_command']
        )
        assert new_permissions['send_command'] == expected_send_command


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestPatchInvalid(PermissionsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'patch'

    REQUEST_CONTENT = [
        ({'json': {'send_message': (42,)}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'send_message': None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'date_modified': None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': '{"api": true}'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, permissions, content, status):
        # set the etag
        content.setdefault('headers', {}).update(
            {'If-Match': permissions.headers['ETag']}
        )

        response = client.patch(
            f'/slurk/api/permissions/{permissions.json["id"]}', **content
        )
        assert response.status_code == status, parse_error(response)
