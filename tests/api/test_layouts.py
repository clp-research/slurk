# -*- coding: utf-8 -*-
"""Test requests to the `layout` table."""

from http import HTTPStatus
import json
import logging
import os

import pytest

from .. import parse_error
from tests.api import InvalidWithEtagTemplate, RequestOptionsTemplate


PREFIX = f'{__name__.replace(".", os.sep)}.py'


class LayoutsTable:
    @property
    def table_name(self):
        return 'layouts'


class TestRequestOptions(LayoutsTable, RequestOptionsTemplate):
    pass


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option[GET]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestGetValid:
    def test_valid_request(self, client, layouts):
        response = client.get('/slurk/api/layouts')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the posted table instance is included
        def retr_by_id(inst):
            return inst['id'] == layouts.json['id']

        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == layouts.json

        # check that the `get` request did not alter the database
        response = client.get(
            '/slurk/api/layouts', headers={'If-None-Match': response.headers['ETag']}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(on=[f'{PREFIX}::TestRequestOptions::test_request_option[POST]'])
class TestPostValid:
    REQUEST_CONTENT = [
        {'json': {'title': 'Test Room'}},
        {
            'json': {
                'title': 'Test Room',
                'read_only': True,
                'show_latency': False,
                'show_users': False,
            }
        },
        {
            'data': {'title': 'Test Room', 'show_latency': False},
            'headers': {'Content-Type': 'application/json'},
        },
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, content):
        data = content.get('json', {}) or content.get('data', {})
        # serialize data content to json
        if 'data' in content:
            content['data'] = json.dumps(content['data'])

        response = client.post('/slurk/api/layouts', **content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        layout = response.json
        assert layout['date_modified'] is None

        assert layout['title'] == data.get('title')
        assert layout['subtitle'] == data.get('subtitle', None)
        assert layout['show_users'] == data.get('show_users', True)
        assert layout['show_latency'] == data.get('show_latency', True)
        assert layout['read_only'] == data.get('read_only', False)
        assert layout['script'] is None
        assert layout['html'] == ''
        assert layout['css'] == ''

    HTML = [
        # special tag
        ({'layout-type': 'br'}, '<br>\n'),
        # tag and content without attributes
        (
            {'layout-type': 'div', 'layout-content': 'Sample Text'},
            '<div>\n    Sample Text\n</div>\n',
        ),
        # several attributes
        (
            {'layout-type': 'img', 'src': 'some.gif', 'alt': 'Some Gif'},
            (
                "<img src='some.gif' alt='Some Gif' />\n",
                "<img alt='Some Gif' src='some.gif' />\n",
            ),
        ),
        # nested structure with attributes
        (
            {
                'layout-type': 'div',
                'layout-content': [
                    {
                        'layout-type': 'h1',
                        'layout-content': 'Headline',
                        'style': 'color: #287fd6;',
                    }
                ],
                'style': 'color: #abb2b9;',
            },
            "<div style='color: #abb2b9;'>\n    <h1 style='color: #287fd6;'>"
            "\n        Headline\n    </h1>\n</div>\n",
        ),
    ]

    @pytest.mark.parametrize('content, html', HTML)
    def test_json_to_html_translation(self, client, content, html):
        content = {'title': 'Test Room', 'html': [content]}

        # layout passed as python dictionary to `json` key
        response = client.post('/slurk/api/layouts', json=content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        if isinstance(html, tuple):
            assert response.json['html'] in html
        else:
            assert response.json['html'] == html

        # layout passed as json to `data` key
        response = client.post(
            '/slurk/api/layouts',
            data=json.dumps(content),
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        if isinstance(html, tuple):
            assert response.json['html'] in html
        else:
            assert response.json['html'] == html

    CSS = [
        (
            {'h1': {'color': 'blue', 'font-family': 'verdana', 'font-size': '300%'}},
            'h1 {\n    color: blue;\n    font-family: verdana;\n    font-size: 300%;\n}\n\n',
        )
    ]

    @pytest.mark.parametrize('content, css', CSS)
    def test_json_to_css_translation(self, client, content, css):
        content = {'title': 'Test Room', 'css': content}

        # layout passed a python dictionary to `json` key
        response = client.post('/slurk/api/layouts', json=content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)
        assert response.json['css'] == css

        # layout passed as json to `data` key
        response = client.post(
            '/slurk/api/layouts',
            data=json.dumps(content),
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)
        assert response.json['css'] == css

    SCRIPTS = [
        (
            {
                'incoming-text': 'display-text',
                'incoming-image': 'display-image',
                'submit-message': 'send-message',
                'print-history': 'plain-history',
                'typing-users': 'typing-users',
            },
            # substring that indicates that a layout was successfully inserted
            (
                'incoming_text',
                'incoming_image',
                'keypress',
                'print_history',
                'update_typing',
            ),
        ),
        ({'plain': ['ask-reload']}, ('window.onbeforeunload',)),
    ]

    @pytest.mark.parametrize('content, scripts', SCRIPTS)
    def test_script_insertion(self, client, content, scripts):
        content = {'title': 'Test Room', 'scripts': content}

        # layout passed a python dictionary to `json` key
        response = client.post('/slurk/api/layouts', json=content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)
        # check that the created script includes a variable for each specified script
        assert all([(s in response.json['script']) for s in scripts])

        # layout passed as json to `data` key
        response = client.post(
            '/slurk/api/layouts',
            data=json.dumps(content),
            headers={'Content-Type': 'application/json'},
        )
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)
        assert all([(s in response.json['script']) for s in scripts])


@pytest.mark.depends(on=[f'{PREFIX}::TestRequestOptions::test_request_option[POST]'])
class TestPostInvalid:
    REQUEST_CONTENT = [
        ({}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {'json': {'title': 'Test Room', 'show_latency': None}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {'json': {'title': 'Test Room', 'scripts': {'plain': [42]}}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {'json': {'title': 'Test Room', 'scripts': []}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {'json': {'title': 'Test Room', 'html_obj': []}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, content, status):
        response = client.post('/slurk/api/layouts', **content)
        assert response.status_code == status, parse_error(response)

    def test_invalid_scripts(self, client, caplog):
        with caplog.at_level(logging.WARNING):
            client.post(
                '/slurk/api/layouts',
                json={
                    'title': 'Test Room',
                    'scripts': {'incoming-text': 'not-existing'},
                },
            )
        assert 'Could not find script' in caplog.text

    @pytest.mark.depends(on=['tests/api/test_tokens.py::TestPostValid'])
    def test_unauthorized_access(self, client, tokens):
        response = client.post(
            '/slurk/api/layouts',
            json={'title': 'Test Room'},
            headers={'Authorization': f'Bearer {tokens.json["id"]}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client):
        response = client.post(
            '/slurk/api/layouts',
            json={'title': 'Test Room'},
            headers={'Authorization': 'Bearer invalid_token'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestGetIdValid:
    def test_valid_request(self, client, layouts):
        response = client.get(f'/slurk/api/layouts/{layouts.json["id"]}')
        assert response.status_code == HTTPStatus.OK, parse_error(response)
        assert response.json == layouts.json

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/layouts/{layouts.json["id"]}',
            headers={'If-None-Match': response.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestGetIdInvalid:
    def test_not_existing(self, client):
        response = client.get('/slurk/api/layouts/invalid_id')
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestPutValid:
    REQUEST_CONTENT = [
        {'json': {'title': 'Another Room', 'css': {'h1': {'color': 'blue'}}}},
        {
            'data': {'title': 'Another Room'},
            'headers': {'Content-Type': 'application/json'},
        },
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, content, layouts):
        data = content.get('json', {}) or content.get('data', {})
        # serialize data content to json
        if 'data' in content:
            content['data'] = json.dumps(content['data'])
        # set the etag
        content.setdefault('headers', {}).update({'If-Match': layouts.headers['ETag']})

        response = client.put(f'/slurk/api/layouts/{layouts.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_layout = response.json

        # check that a modification was performed
        assert new_layout['id'] == layouts.json['id']
        assert new_layout['date_created'] == layouts.json['date_created']
        assert response.json['date_modified'] is not None
        assert response.headers['ETag'] != layouts.headers['ETag']

        assert new_layout['date_created'] == layouts.json['date_created']
        assert new_layout['id'] == layouts.json['id']
        assert new_layout['title'] == data.get('title')
        assert new_layout['subtitle'] == data.get('subtitle')
        assert new_layout['show_users'] == data.get('show_users', True)
        assert new_layout['show_latency'] == data.get('show_latency', True)
        assert new_layout['read_only'] == data.get('read_only', False)

        # if specified the attribute should have been changed
        assert 'scripts' not in data or new_layout['script'] != layouts.json['script']
        assert 'html' not in data or new_layout['html'] != layouts.json['html']
        assert 'css' not in data or new_layout['css'] != layouts.json['css']


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestPutInvalid(LayoutsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'put'

    def json(self, request):
        return {'json': {'title': 'Test Room'}}

    REQUEST_CONTENT = [
        ({'json': {'subtitle': 'Room for testing'}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {'json': {'title': 'Test Room', 'scripts': {'plain': 'script'}}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {'json': {'title': 'Test Room', 'css_obj': {'h1': {'color': 'blue'}}}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, layouts, content, status):
        # set the etag
        content.setdefault('headers', {}).update({'If-Match': layouts.headers['ETag']})

        response = client.put(f'/slurk/api/layouts/{layouts.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestDeleteValid:
    def test_valid_request(self, client, layouts):
        response = client.delete(
            f'/slurk/api/layouts/{layouts.json["id"]}',
            headers={'If-Match': layouts.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestDeleteInvalid(LayoutsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'delete'

    @pytest.mark.depends(
        on=[
            'tests/api/test_rooms.py::TestPostValid',
            'tests/api/test_rooms.py::TestDeleteValid',
        ]
    )
    def test_deletion_of_layout_in_room(self, client, layouts):
        # create room that uses the layout
        room = client.post('/slurk/api/rooms', json={'layout_id': layouts.json['id']})
        # the deletion of a layout entry that is in use should fail
        response = client.delete(
            f'/slurk/api/layouts/{layouts.json["id"]}',
            headers={'If-Match': layouts.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
            response
        )

        # free the layout entry by deleting the room
        client.delete(
            f'/slurk/api/rooms/{room.json["id"]}',
            headers={'If-Match': room.headers['ETag']},
        )
        # now one should be able to delete the permissions
        response = client.delete(
            f'/slurk/api/layouts/{layouts.json["id"]}',
            headers={'If-Match': layouts.headers['ETag']},
        )

        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)

    @pytest.mark.depends(
        on=[
            'tests/api/test_tasks.py::TestPostValid',
            'tests/api/test_tasks.py::TestDeleteValid',
        ]
    )
    def test_deletion_of_layout_in_task(self, client, layouts):
        task = client.post(
            '/slurk/api/tasks',
            json={'num_users': 3, 'name': 'Test Task', 'layout_id': layouts.json['id']},
        )
        response = client.delete(
            f'/slurk/api/layouts/{layouts.json["id"]}',
            headers={'If-Match': layouts.headers['ETag']},
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
            response
        )

        client.delete(
            f'/slurk/api/tasks/{task.json["id"]}',
            headers={'If-Match': task.headers['ETag']},
        )
        response = client.delete(
            f'/slurk/api/layouts/{layouts.json["id"]}',
            headers={'If-Match': layouts.headers['ETag']},
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
        {'json': {'title': 'More Tests', 'subtitle': 'Room for testing'}},
        {'json': {'show_latency': True, 'read_only': True}},
        {'json': {'scripts': {'incoming-text': 'display-text'}}},
        {'json': {'html': [{'layout-type': 'br'}]}},
        {'json': {'css': {'h1': {'color': 'blue'}}}},
        {'json': {'subtitle': None}},
    ]

    @pytest.mark.parametrize('content', REQUEST_CONTENT)
    def test_valid_request(self, client, content, layouts):
        data = content.get('json', {}) or content.get('data', {})

        # set the etag
        content.setdefault('headers', {}).update({'If-Match': layouts.headers['ETag']})

        response = client.patch(f'/slurk/api/layouts/{layouts.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_layout = response.json
        # check that a modification was performed without creating new table entry
        assert new_layout['id'] == layouts.json['id']
        assert new_layout['date_created'] == layouts.json['date_created']
        assert response.json['date_modified'] is not None
        assert response.headers['ETag'] != layouts.headers['ETag']

        expected_title = data.get('title', layouts.json['title'])
        assert new_layout['title'] == expected_title
        expected_subtitle = data.get('subtitle', layouts.json['subtitle'])
        assert new_layout['subtitle'] == expected_subtitle
        expected_show_users = data.get('show_users', layouts.json['show_users'])
        assert new_layout['show_users'] == expected_show_users
        expected_show_latency = data.get('show_latency', layouts.json['show_latency'])
        assert new_layout['show_latency'] == expected_show_latency
        expected_read_only = data.get('read_only', layouts.json['read_only'])
        assert new_layout['read_only'] == expected_read_only

        # if specified the attribute should have been changed
        assert 'scripts' not in data or new_layout['script'] != layouts.json['script']
        assert 'html' not in data or new_layout['html'] != layouts.json['html']
        assert 'css' not in data or new_layout['css'] != layouts.json['css']


@pytest.mark.depends(
    on=[
        f'{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]',
        f'{PREFIX}::TestPostValid',
    ]
)
class TestPatchInvalid(LayoutsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return 'patch'

    REQUEST_CONTENT = [
        ({'json': {'id': 1}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'title': None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'json': {'show_latency': 42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {'json': {'html_obj': [{'layout-type': 'br'}]}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        ({'json': {'html': '<br>'}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'data': {'title': 'Another Test Room'}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
        ({'data': '{"title": "Another Test Room"}'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize('content, status', REQUEST_CONTENT)
    def test_invalid_request(self, client, layouts, content, status):
        # set the etag
        content.setdefault('headers', {}).update({'If-Match': layouts.headers['ETag']})

        response = client.patch(f'/slurk/api/layouts/{layouts.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)
