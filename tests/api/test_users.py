# -*- coding: utf-8 -*-
"""Test requests to the `users` table."""

from copy import deepcopy
from http import HTTPStatus
import json
import os
from unittest import mock

import pytest

from .. import parse_error
from tests.api import InvalidTemplate, InvalidWithEtagTemplate, RequestOptionsTemplate


PREFIX = f'{__name__.replace(".", os.sep)}.py'


def mock_request_as_active_user(app, obj, method, argument_scheme, status):
    original_method_copy = deepcopy(getattr(obj, method).__wrapped__)

    from slurk.views.api.rooms import blp, UserSchema

    @blp.query("user", UserSchema, check_etag=False)
    @blp.arguments(argument_scheme, as_kwargs=True)
    @blp.response(status)
    @blp.login_required
    def mock_func(*args, user, **kwargs):
        # this mock is necessary in order to stop the database
        # from being updated with the changed attribute
        with mock.patch("slurk.views.api.rooms.Log"):
            user.session_id = "valid_id"
            original_method_copy(*args, user=user, **kwargs)
            user.session_id = None

    return mock.patch.object(obj, method, new=mock_func)


class UsersTable:
    @property
    def table_name(self):
        return "users"


class TestRequestOptions(UsersTable, RequestOptionsTemplate):
    @pytest.mark.depends(on=[f"{PREFIX}::TestPostValid"])
    @pytest.mark.parametrize("option", ["PATCH"])
    def test_request_option_with_id_attribute(self, client, option, users):
        for attribute_on in {"class", "id", "element"}:
            response = client.options(
                f'/slurk/api/users/{users.json["id"]}/attribute/{attribute_on}/test-field'
            )
            assert response.status_code == HTTPStatus.OK
            assert (
                option in response.headers["Allow"]
            ), HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(on=[f"{PREFIX}::TestPostValid"])
    @pytest.mark.parametrize("option", ["POST", "DELETE"])
    def test_request_option_with_id_class(self, client, option, users):
        response = client.options(
            f'/slurk/api/users/{users.json["id"]}/class/test-field'
        )
        assert response.status_code == HTTPStatus.OK
        assert (
            option in response.headers["Allow"]
        ), HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(on=[f"{PREFIX}::TestPostValid"])
    @pytest.mark.parametrize("option", ["PATCH"])
    def test_request_option_with_id_text(self, client, option, users):
        response = client.options(
            f'/slurk/api/users/{users.json["id"]}/text/test-field'
        )
        assert response.status_code == HTTPStatus.OK
        assert (
            option in response.headers["Allow"]
        ), HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(
        on=[f"{PREFIX}::TestPostValid", "tests/api/test_rooms.py::TestPostValid"]
    )
    @pytest.mark.parametrize("option", ["POST", "DELETE"])
    def test_request_option_with_id_room(self, client, option, users, rooms):
        response = client.options(
            f'/slurk/api/users/{users.json["id"]}/rooms/{rooms.json["id"]}'
        )
        assert response.status_code == HTTPStatus.OK
        assert (
            option in response.headers["Allow"]
        ), HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.depends(on=[f"{PREFIX}::TestPostValid"])
    @pytest.mark.parametrize("option", ["GET"])
    def test_request_option_with_id_rooms(self, client, option, users):
        response = client.options(f'/slurk/api/users/{users.json["id"]}/rooms')
        assert response.status_code == HTTPStatus.OK
        assert (
            option in response.headers["Allow"]
        ), HTTPStatus.METHOD_NOT_ALLOWED.description


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetValid:
    def test_valid_request(self, client, users):
        response = client.get("/slurk/api/users")
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the posted table instance is included
        def retr_by_id(inst):
            return inst["id"] == users.json["id"]

        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == users.json

        # check that the `get` request did not alter the database
        response = client.get(
            "/slurk/api/users", headers={"If-None-Match": response.headers["ETag"]}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        "tests/api/test_tokens.py::TestPostValid",
        "tests/api/test_tokens.py::TestGetValid",
    ]
)
class TestPostValid:
    def test_token_limited_registrations(self, client, tokens):
        response = client.post(
            "/slurk/api/users",
            json={"name": "Test User", "token_id": tokens.json["id"]},
        )
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        users = response.json
        assert users["date_modified"] is None
        tokens = client.get(f'/slurk/api/tokens/{tokens.json["id"]}')
        assert tokens.status_code == HTTPStatus.OK, parse_error(tokens)
        assert tokens.json["registrations_left"] == 0

        users["name"] == "Test User"
        users["session_id"] is None

    def test_token_unlimited_registrations(self, client, permissions, rooms):
        tokens = client.post(
            "/slurk/api/tokens",
            json={
                "permissions_id": permissions.json["id"],
                "room_id": rooms.json["id"],
                "registrations_left": -1,
            },
        )
        assert tokens.status_code == HTTPStatus.CREATED, parse_error(tokens)
        response = client.post(
            "/slurk/api/users",
            json={"name": "Another Test User", "token_id": tokens.json["id"]},
        )
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        users = response.json
        assert users["date_modified"] is None
        tokens = client.get(f'/slurk/api/tokens/{tokens.json["id"]}')
        assert tokens.status_code == HTTPStatus.OK, parse_error(tokens)
        assert tokens.json["registrations_left"] == -1

        users["name"] == "Another Test User"
        users["session_id"] is None


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        "tests/api/test_tokens.py::TestPostValid",
    ]
)
class TestPostInvalid:
    REQUEST_CONTENT = [
        ({"json": {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"name": "Test User"}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"name": "Test User", "token_id": -42}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, content, status, permissions):
        response = client.post("/slurk/api/users", **content)
        assert response.status_code == status, parse_error(response)

    def test_token_no_registrations_left(self, client, tokens):
        # use the only one registration
        response = client.post(
            "/slurk/api/users",
            json={"name": "Test User", "token_id": tokens.json["id"]},
        )
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)
        # attempt another registration
        response = client.post(
            "/slurk/api/users",
            json={"name": "Another Test User", "token_id": tokens.json["id"]},
        )
        response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(response)

    def test_token_no_assigned_room(self, client, admin_token):
        response = client.post(
            "/slurk/api/users",
            json={"name": "Another Test User", "token_id": admin_token},
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
            response
        )

    def test_unauthorized_access(self, client, tokens):
        response = client.post(
            "/slurk/api/users",
            json={"name": "Test User", "token_id": tokens.json["id"]},
            headers={"Authorization": f'Bearer {tokens.json["id"]}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client, tokens):
        response = client.post(
            "/slurk/api/users",
            json={"name": "Test User", "token_id": tokens.json["id"]},
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetIdValid:
    def test_valid_request(self, client, users):
        response = client.get(f'/slurk/api/users/{users.json["id"]}')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        assert response.json == users.json

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/users/{users.json["id"]}',
            headers={"If-None-Match": response.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[f"{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]"]
)
class TestGetIdInvalid:
    def test_not_existing(self, client):
        response = client.get("/slurk/api/users/invalid_id")
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]",
        "tests/api/test_permissions.py::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
        "tests/api/test_tokens.py::TestPostValid",
        "tests/api/test_tokens.py::TestGetValid",
    ]
)
class TestPutValid:
    def test_valid_request(self, client, users, permissions, rooms):
        tokens = client.post(
            "/slurk/api/tokens",
            json={
                "permissions_id": permissions.json["id"],
                "room_id": rooms.json["id"],
                "registrations_left": 3,
            },
        )
        assert tokens.status_code == HTTPStatus.CREATED, parse_error(tokens)
        response = client.put(
            f'/slurk/api/users/{users.json["id"]}',
            json={"name": "", "token_id": tokens.json["id"]},
            headers={"If-Match": users.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_users = response.json
        # check that a modification was performed without creating new table entry
        assert new_users["id"] == users.json["id"]
        assert new_users["date_created"] == users.json["date_created"]
        assert new_users["date_modified"] is not None
        assert response.headers["ETag"] != users.headers["ETag"]

        new_users["name"] == ""
        new_users["session_id"] is None

        tokens = client.get(f'/slurk/api/tokens/{tokens.json["id"]}')
        assert tokens.status_code == HTTPStatus.OK, parse_error(tokens)
        assert tokens.json["registrations_left"] == 2


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_permissions.py::TestPostValid",
        "tests/api/test_tokens.py::TestPostValid",
        "tests/api/test_tokens.py::TestGetValid",
    ]
)
class TestPutInvalid(UsersTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "put"

    def json(self, request):
        tokens = request.getfixturevalue("tokens")
        return {"json": {"name": "Test User", "token_id": tokens.json["id"]}}

    REQUEST_CONTENT = [
        ({"json": {"name": "Test User"}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"name": None, "token_id": -1}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"name": "Test User", "token_id": -1}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, users, content, status, permissions, rooms):
        tokens = client.post(
            "/slurk/api/tokens",
            json={
                "permissions_id": permissions.json["id"],
                "room_id": rooms.json["id"],
                "registrations_left": 0,
            },
        )
        assert tokens.status_code == HTTPStatus.CREATED, parse_error(tokens)
        if content["json"].get("token_id") == -1:
            content["json"]["token_id"] = tokens.json["id"]
        # set the etag
        content.setdefault("headers", {}).update({"If-Match": users.headers["ETag"]})

        response = client.put(f'/slurk/api/users/{users.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteValid:
    def test_valid_request(self, client, users):
        response = client.delete(
            f'/slurk/api/users/{users.json["id"]}',
            headers={"If-Match": users.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteInvalid(UsersTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "delete"

    @pytest.mark.depends(
        on=[
            "tests/api/test_logs.py::TestPostValid",
            "tests/api/test_logs.py::TestDeleteValid",
        ]
    )
    def test_deletion_of_user_in_logs(self, client, users):
        # create logs that use the user
        log = client.post(
            "/slurk/api/logs", json={"event": "Test Event", "user_id": users.json["id"]}
        )
        response = client.delete(
            f'/slurk/api/users/{users.json["id"]}',
            headers={"If-Match": users.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)

        # Check if the log entry is deleted
        response = client.get(f'/slurk/api/logs/{log.json["id"]}')
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchValid:
    def test_valid_request(self, client, users, tokens):
        response = client.patch(
            f'/slurk/api/users/{users.json["id"]}',
            json={"name": "Another Test User"},
            headers={"If-Match": users.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_users = response.json
        # check that a modification was performed without creating new table entry
        assert new_users["id"] == users.json["id"]
        assert new_users["date_created"] == users.json["date_created"]
        assert new_users["date_modified"] is not None
        assert response.headers["ETag"] != users.headers["ETag"]

        new_users["name"] == "Another Test User"
        new_users["session_id"] is None

        tokens = client.get(f'/slurk/api/tokens/{tokens.json["id"]}')
        assert tokens.status_code == HTTPStatus.OK, parse_error(tokens)
        # zero as this token was already used in the user before
        assert tokens.json["registrations_left"] == 0


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchInvalid(UsersTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "patch"

    def test_token_no_registrations_left(self, client, users, tokens):
        # use the only one registration
        response = client.patch(
            f'/slurk/api/users/{users.json["id"]}',
            json={"name": "Test User", "token_id": tokens.json["id"]},
            headers={"If-Match": users.headers["ETag"]},
        )
        response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(response)

    def test_token_no_assigned_room(self, client, users, admin_token):
        response = client.patch(
            f'/slurk/api/users/{users.json["id"]}',
            json={"name": "Another Test User", "token_id": admin_token},
            headers={"If-Match": users.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
            response
        )


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_attribute[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchAttributeValid:
    REQUEST_CONTENT = [
        ({"json": {"attribute": "color", "value": "red"}}, "id"),
        ({"json": {"attribute": "background-color", "value": "yellow"}}, "class"),
        ({"json": {"attribute": "font-size", "value": "30px"}}, "element"),
    ]

    @pytest.mark.parametrize("content, attribute_on", REQUEST_CONTENT)
    def test_valid_request_id(self, app, client, users, content, attribute_on):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get("json", {}) or content.get("data", {})

            with app.app_context():
                from slurk.views.api.rooms import (
                    AttributeSchema,
                    UserAttributeId,
                    UserAttributeClass,
                    UserAttributeElement,
                )

                str_to_cls = {
                    "id": UserAttributeId,
                    "class": UserAttributeClass,
                    "element": UserAttributeElement,
                }
                with mock_request_as_active_user(
                    app, str_to_cls[attribute_on], "patch", AttributeSchema, 204
                ):
                    response = client.patch(
                        f'/slurk/api/users/{users.json["id"]}/attribute/{attribute_on}/test-field',
                        **content,
                    )
                assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(
                    response
                )
                # check that event was triggered
                socketio_mock.assert_called_with(
                    "attribute_update",
                    {
                        **data,
                        "cls"
                        if attribute_on == "class"
                        else attribute_on: "test-field",
                    },
                    room="valid_id",
                )


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_attribute[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchAttributeInvalid(UsersTable, InvalidTemplate):
    @property
    def request_method(self):
        return "patch"

    def url_extension(self, request):
        # test for only one of the three objects one can alter features on
        return "/attribute/class/test-field"

    def json(self, request):
        return {"json": {"attribute": "background-color", "value": "yellow"}}

    REQUEST_CONTENT = [
        ({"json": {"other": "test"}}, "id", HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"attribute": "font-size", "value": 30}},
            "id",
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"attribute": None, "value": "yellow"}},
            "class",
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"data": {"attribute": "color", "value": "red"}},
            "element",
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        ),
    ]

    @pytest.mark.parametrize("content, attribute_on, status", REQUEST_CONTENT)
    def test_invalid_request(self, app, client, users, content, attribute_on, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            with app.app_context():
                from slurk.views.api.rooms import (
                    AttributeSchema,
                    UserAttributeId,
                    UserAttributeClass,
                    UserAttributeElement,
                )

                str_to_cls = {
                    "id": UserAttributeId,
                    "class": UserAttributeClass,
                    "element": UserAttributeElement,
                }
                with mock_request_as_active_user(
                    app, str_to_cls[attribute_on], "patch", AttributeSchema, 204
                ):
                    response = client.patch(
                        f'/slurk/api/users/{users.json["id"]}/attribute/{attribute_on}/test-field',
                        **content,
                    )
            assert response.status_code == status, parse_error(response)
            # check that event was not triggered
            socketio_mock.assert_not_called()

    def test_inactive_user(self, client, users):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.patch(
                f'/slurk/api/users/{users.json["id"]}/attribute/class/test-field',
                json={"attribute": "background-color", "value": "yellow"},
            )
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
                response
            )
            # check that event was not triggered
            socketio_mock.assert_not_called()


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_class[POST]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPostClassValid:
    REQUEST_CONTENT = [
        {"json": {"class": "test"}},
        {"data": {"class": "test"}, "headers": {"Content-Type": "application/json"}},
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, app, client, users, content):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get("json", {}) or content.get("data", {})

            # convert dictionary to json
            if "data" in content:
                content["data"] = json.dumps(content["data"])

            with app.app_context():
                from slurk.views.api.rooms import ClassSchema, UserClass

                with mock_request_as_active_user(
                    app, UserClass, "post", ClassSchema, 204
                ):
                    response = client.post(
                        f'/slurk/api/users/{users.json["id"]}/class/test-field',
                        **content,
                    )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            # check that event was triggered
            socketio_mock.assert_called_with(
                "class_add", {**data, "id": "test-field"}, room="valid_id"
            )


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_class[POST]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPostClassInvalid(UsersTable, InvalidTemplate):
    @property
    def request_method(self):
        return "post"

    def url_extension(self, request):
        return "/class/test-field"

    def json(self, request):
        return {"json": {"class": "test"}}

    REQUEST_CONTENT = [
        ({"json": {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"class": None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"data": {"class": "test"}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, app, client, users, content, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            with app.app_context():
                from slurk.views.api.rooms import ClassSchema, UserClass

                with mock_request_as_active_user(
                    app, UserClass, "post", ClassSchema, 204
                ):
                    response = client.post(
                        f'/slurk/api/users/{users.json["id"]}/class/test-field',
                        **content,
                    )
            assert response.status_code == status, parse_error(response)
            # check that event was not triggered
            socketio_mock.assert_not_called()

    def test_inactive_user(self, client, users):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.post(
                f'/slurk/api/users/{users.json["id"]}/class/test-field',
                json={"class": "test"},
            )
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
                response
            )
            # check that event was not triggered
            socketio_mock.assert_not_called()


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_class[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteClassValid:
    REQUEST_CONTENT = [
        {"json": {"class": "test"}},
        {"data": {"class": "test"}, "headers": {"Content-Type": "application/json"}},
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, app, client, users, content):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get("json", {}) or content.get("data", {})

            # convert dictionary to json
            if "data" in content:
                content["data"] = json.dumps(content["data"])
            with app.app_context():
                from slurk.views.api.rooms import ClassSchema, UserClass

                with mock_request_as_active_user(
                    app, UserClass, "delete", ClassSchema, 204
                ):
                    response = client.delete(
                        f'/slurk/api/users/{users.json["id"]}/class/test-field',
                        **content,
                    )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            # check that event was triggered
            socketio_mock.assert_called_with(
                "class_remove", {**data, "id": "test-field"}, room="valid_id"
            )


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_class[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteClassInvalid(UsersTable, InvalidTemplate):
    @property
    def request_method(self):
        return "delete"

    def url_extension(self, request):
        return "/class/test-field"

    def json(self, request):
        return {"json": {"class": "test"}}

    REQUEST_CONTENT = [
        ({"json": {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"class": []}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"data": {"class": "test"}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, app, client, users, content, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            with app.app_context():
                from slurk.views.api.rooms import ClassSchema, UserClass

                with mock_request_as_active_user(
                    app, UserClass, "delete", ClassSchema, 204
                ):
                    response = client.delete(
                        f'slurk/api/users/{users.json["id"]}/class/test-field',
                        **content,
                    )
            assert response.status_code == status, parse_error(response)
            # check that event was not triggered
            socketio_mock.assert_not_called()

    def test_inactive_user(self, client, users):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.delete(
                f'/slurk/api/users/{users.json["id"]}/class/test-field',
                json={"class": "test"},
            )
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
                response
            )
            # check that event was not triggered
            socketio_mock.assert_not_called()


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_rooms[GET]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestGetRoomsByUserValid:
    def test_valid_request(self, client, users, rooms):
        response = client.get(f'/slurk/api/users/{users.json["id"]}/rooms')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the room assigned on user creation is included
        assert response.json == [rooms.json]

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/users/{users.json["id"]}/rooms',
            headers={"If-None-Match": response.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_room[POST]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestPostRoomValid:
    def test_valid_request(self, app, client, users, rooms):
        with mock.patch("slurk.models.user.User.join_room") as join_room_mock:
            response = client.post(
                f'/slurk/api/users/{users.json["id"]}/rooms/{rooms.json["id"]}'
            )
            assert response.status_code == HTTPStatus.CREATED, parse_error(response)
            assert join_room_mock.called


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_room[POST]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestPostRoomInvalid(UsersTable, InvalidTemplate):
    @property
    def request_method(self):
        return "post"

    def url_extension(self, request):
        rooms = request.getfixturevalue("rooms")
        return f'/rooms/{rooms.json["id"]}'

    def test_not_existing_room(self, client, users):
        response = client.post(
            f'/slurk/api/users/{users.json["id"]}/rooms/invalid_id',
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_room[DELETE]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestDeleteRoomValid:
    def test_valid_request(self, app, client, users, rooms):
        with mock.patch("slurk.models.user.User.leave_room") as leave_room_mock:
            response = client.delete(
                f'/slurk/api/users/{users.json["id"]}/rooms/{rooms.json["id"]}',
                headers={"If-Match": users.headers["ETag"]},
            )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            assert leave_room_mock.called


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_room[DELETE]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestDeleteRoomInvalid(UsersTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "delete"

    def url_extension(self, request):
        rooms = request.getfixturevalue("rooms")
        return f'/rooms/{rooms.json["id"]}'

    def test_not_existing_room(self, client, users):
        response = client.delete(
            f'/slurk/api/users/{users.json["id"]}/rooms/invalid_id',
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_text[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchTextValid:
    REQUEST_CONTENT = [{"json": {"text": "test"}}]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, app, client, users, content):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            data = content.get("json", {}) or content.get("data", {})
            with app.app_context():
                from slurk.views.api.rooms import TextSchema, UserText

                with mock_request_as_active_user(
                    app, UserText, "patch", TextSchema, 204
                ):
                    response = client.patch(
                        f'/slurk/api/users/{users.json["id"]}/text/test-field',
                        **content,
                    )
            assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)
            # check that event was triggered
            socketio_mock.assert_called_with(
                "text_update", {**data, "id": "test-field"}, room="valid_id"
            )


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id_text[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchTextInvalid(UsersTable, InvalidTemplate):
    @property
    def request_method(self):
        return "patch"

    def url_extension(self, request):
        return "/text/test-field"

    def json(self, request):
        return {"json": {"text": "test"}}

    REQUEST_CONTENT = [
        ({"json": {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"text": 42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"class": "div"}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"data": {"text": "test"}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, app, client, users, content, status):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            with app.app_context():
                from slurk.views.api.rooms import TextSchema, UserText

                with mock_request_as_active_user(
                    app, UserText, "patch", TextSchema, 204
                ):
                    response = client.patch(
                        f'/slurk/api/users/{users.json["id"]}/text/test-field',
                        **content,
                    )
            assert response.status_code == status, parse_error(response)
            socketio_mock.assert_not_called()

    def test_inactive_user(self, app, client, users):
        with mock.patch("slurk.views.api.rooms.socketio.emit") as socketio_mock:
            response = client.patch(
                f'/slurk/api/users/{users.json["id"]}/text/test-field',
                json={"text": "test"},
            )
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
                response
            )
            # check that event was not triggered
            socketio_mock.assert_not_called()
