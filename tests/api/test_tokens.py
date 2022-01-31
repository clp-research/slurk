# -*- coding: utf-8 -*-
"""Test requests to the `tokens` table."""

from http import HTTPStatus
import json
import os

import pytest

from .. import parse_error
from tests.api import InvalidWithEtagTemplate, RequestOptionsTemplate


PREFIX = f'{__name__.replace(".", os.sep)}.py'


class TokensTable:
    @property
    def table_name(self):
        return "tokens"


class TestRequestOptions(TokensTable, RequestOptionsTemplate):
    pass


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetValid:
    def test_valid_request(self, client, tokens):
        response = client.get("/slurk/api/tokens")
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the posted table instance is included
        def retr_by_id(inst):
            return inst["id"] == tokens.json["id"]

        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == tokens.json

        # check that the `get` request did not alter the database
        response = client.get(
            "/slurk/api/tokens", headers={"If-None-Match": response.headers["ETag"]}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        "tests/api/test_permissions.py::TestPostValid",
        "tests/api/test_tasks.py::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestPostValid:
    REQUEST_CONTENT = [
        {"json": {"permissions_id": -1}},
        {"json": {"permissions_id": -1, "registrations_left": 3, "task_id": -1}},
        {"json": {"permissions_id": -1, "room_id": -1, "task_id": -1}},
        {
            "data": {"permissions_id": -1},
            "headers": {"Content-Type": "application/json"},
        },
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, content, permissions, rooms, tasks):
        # replace placeholder ids with valid ones
        for key in content:
            if content[key].get("permissions_id") == -1:
                content[key]["permissions_id"] = permissions.json["id"]
            if content[key].get("room_id") == -1:
                content[key]["room_id"] = rooms.json["id"]
            if content[key].get("task_id") == -1:
                content[key]["task_id"] = tasks.json["id"]
        data = content.get("json", {}) or content.get("data", {})

        # convert dictionary to json
        if "data" in content:
            content["data"] = json.dumps(content["data"])

        response = client.post("/slurk/api/tokens", **content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        token = response.json
        assert token["date_modified"] is None

        assert token["permissions_id"] == data.get("permissions_id")
        assert token["registrations_left"] == data.get("registrations_left", 1)
        assert token["task_id"] == data.get("task_id", None)
        assert token["room_id"] == data.get("room_id", None)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        "tests/api/test_permissions.py::TestPostValid",
    ]
)
class TestPostInvalid:
    REQUEST_CONTENT = [
        ({"json": {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"permissions_id": -1, "registrations_left": -2}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"permissions_id": -1, "room_id": -42}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"permissions_id": -1, "task_id": "Test Task"}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        ({"data": {"permissions_id": -1}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, content, status, permissions):
        # replace placeholder ids with valid ones
        for key in content:
            if (
                "permissions_id" in content[key]
                and content[key]["permissions_id"] == -1
            ):
                content[key]["permissions_id"] = permissions.json["id"]
        response = client.post("/slurk/api/tokens", **content)
        assert response.status_code == status, parse_error(response)

    @pytest.mark.depends(on=["tests/api/test_tokens.py::TestPostValid"])
    def test_unauthorized_access(self, client, tokens, permissions):
        response = client.post(
            "/slurk/api/tokens",
            json={"permissions_id": permissions.json["id"]},
            headers={"Authorization": f'Bearer {tokens.json["id"]}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client, permissions):
        response = client.post(
            "/slurk/api/tokens",
            json={"permissions_id": permissions.json["id"]},
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
    def test_valid_request(self, client, tokens):
        response = client.get(f'/slurk/api/tokens/{tokens.json["id"]}')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        assert response.json == tokens.json

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/tokens/{tokens.json["id"]}',
            headers={"If-None-Match": response.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[f"{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]"]
)
class TestGetIdInvalid:
    def test_not_existing(self, client):
        response = client.get("/slurk/api/tokens/invalid_id")
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_permissions.py::TestPostValid",
        "tests/api/test_tasks.py::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestPutValid:
    REQUEST_CONTENT = [
        {"json": {"permissions_id": -1, "registrations_left": -1}},
        {"json": {"permissions_id": -1, "registrations_left": 5, "room_id": -1}},
        {
            "json": {
                "permissions_id": -1,
                "registrations_left": 0,
                "room_id": -1,
                "task_id": -1,
            }
        },
        {
            "data": {"permissions_id": -1, "registrations_left": 1},
            "headers": {"Content-Type": "application/json"},
        },
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, tokens, content, permissions, rooms, tasks):
        # replace placeholder ids with valid ones
        for key in content:
            if content[key].get("permissions_id") == -1:
                content[key]["permissions_id"] = permissions.json["id"]
            if content[key].get("room_id") == -1:
                content[key]["room_id"] = rooms.json["id"]
            if content[key].get("task_id") == -1:
                content[key]["task_id"] = tasks.json["id"]
        data = content.get("json", {}) or content.get("data", {})
        # serialize data content to json
        if "data" in content:
            content["data"] = json.dumps(content["data"])

        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tokens.headers["ETag"]})

        response = client.put(f'/slurk/api/tokens/{tokens.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_tokens = response.json

        # check that a modification was performed
        assert new_tokens["id"] == tokens.json["id"]
        assert new_tokens["date_created"] == tokens.json["date_created"]
        assert response.json["date_modified"] is not None
        assert response.headers["ETag"] != tokens.headers["ETag"]

        assert new_tokens["permissions_id"] == data.get("permissions_id")
        assert new_tokens["registrations_left"] == data.get("registrations_left", 1)
        assert new_tokens["task_id"] == data.get("task_id", None)
        assert new_tokens["room_id"] == data.get("room_id", None)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_permissions.py::TestPostValid",
    ]
)
class TestPutInvalid(TokensTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "put"

    def json(self, request):
        permissions = request.getfixturevalue("permissions")
        return {"json": {"permissions_id": permissions.json["id"]}}

    REQUEST_CONTENT = [
        ({"json": {"permissions_id": None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"permissions_id": -1, "registrations_left": 2**63}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"permissions_id": -1, "task_id": -42}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, tokens, content, status, permissions):
        # replace placeholder ids with valid ones
        for key in content:
            if content[key].get("permissions_id") == -1:
                content[key]["permissions_id"] = permissions.json["id"]

        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tokens.headers["ETag"]})

        response = client.put(f'/slurk/api/tokens/{tokens.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteValid:
    def test_valid_request(self, client, tokens):
        response = client.delete(
            f'/slurk/api/tokens/{tokens.json["id"]}',
            headers={"If-Match": tokens.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteInvalid(TokensTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "delete"

    @pytest.mark.depends(
        on=[
            f"{PREFIX}::TestGetIdValid",
            # TODO 'tests/api/test_users.py::TestPostValid',
            # TODO 'tests/api/test_users.py::TestDeleteValid'
        ]
    )
    def test_deletion_of_token_in_user(self, client, tokens):
        # create user that uses the token
        user = client.post(
            "/slurk/api/users",
            json={"name": "Test User", "token_id": tokens.json["id"]},
        )

        token_uri = f'/slurk/api/tokens/{tokens.json["id"]}'

        # the deletion of a tokens entry that is in use should fail
        response = client.delete(
            token_uri, headers={"If-Match": client.head(token_uri).headers["ETag"]}
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, parse_error(
            response
        )

        # free the token entry by deleting the users
        client.delete(
            f'/slurk/api/users/{user.json["id"]}',
            headers={"If-Match": user.headers["ETag"]},
        )

        # now one should be able to delete the token
        response = client.delete(
            token_uri, headers={"If-Match": client.head(token_uri).headers["ETag"]}
        )

        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_tasks.py::TestPostValid",
    ]
)
class TestPatchValid:
    REQUEST_CONTENT = [
        {"json": {"registrations_left": 0}},
        {"json": {"registrations_left": 2**63 - 1}},
        {"json": {"room_id": None}},
        {"json": {"task_id": -1, "room_id": None}},
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, tokens, content, tasks):
        # replace placeholder ids with valid ones
        for key in content:
            if content[key].get("task_id") == -1:
                content[key]["task_id"] = tasks.json["id"]
        data = content.get("json", {}) or content.get("data", {})

        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tokens.headers["ETag"]})

        response = client.patch(f'/slurk/api/tokens/{tokens.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_tokens = response.json

        # check that a modification was performed without creating new table entry
        assert new_tokens["id"] == tokens.json["id"]
        assert new_tokens["date_created"] == tokens.json["date_created"]
        assert response.json["date_modified"] is not None
        assert response.headers["ETag"] != tokens.headers["ETag"]

        expected_permissions_id = data.get(
            "permissions_id", tokens.json["permissions_id"]
        )
        assert new_tokens["permissions_id"] == expected_permissions_id
        expected_registrations_left = data.get(
            "registrations_left", tokens.json["registrations_left"]
        )
        assert new_tokens["registrations_left"] == expected_registrations_left
        expected_task_id = data.get("task_id", tokens.json["task_id"])
        assert new_tokens["task_id"] == expected_task_id
        expected_room_id = data.get("room_id", tokens.json["room_id"])
        assert new_tokens["room_id"] == expected_room_id


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchInvalid(TokensTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "patch"

    REQUEST_CONTENT = [
        ({"json": {"permissions_id": None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"room_id": -42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"registrations_left": -2}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"id": 2}}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, tokens, content, status):
        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tokens.headers["ETag"]})

        response = client.patch(f'/slurk/api/tokens/{tokens.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)
