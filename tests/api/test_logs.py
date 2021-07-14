# -*- coding: utf-8 -*-
"""Test requests to the `logs` table."""

from http import HTTPStatus
import json
import os

import pytest

from .. import parse_error
from tests.api import InvalidTemplate, InvalidWithEtagTemplate, RequestOptionsTemplate


PREFIX = f'{__name__.replace(".", os.sep)}.py'


class LogsTable:
    @property
    def table_name(self):
        return "logs"


class TestRequestOptions(LogsTable, RequestOptionsTemplate):
    pass


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetValid:
    def test_valid_request(self, client, logs):
        response = client.get("/slurk/api/logs")
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the posted table instance is included
        def retr_by_id(inst):
            return inst["id"] == logs.json["id"]

        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == logs.json

        # check that the `get` request did not alter the database
        response = client.get(
            "/slurk/api/logs", headers={"If-None-Match": response.headers["ETag"]}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetInvalid:
    @pytest.mark.depends(on=["tests/api/test_tokens.py::TestPostValid"])
    def test_unauthorized_access(self, client, tokens):
        response = client.get(
            "/slurk/api/logs", headers={"Authorization": f'Bearer {tokens.json["id"]}'}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client):
        response = client.get(
            "/slurk/api/logs", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        "tests/api/test_users.py::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestPostValid:
    REQUEST_CONTENT = [
        {
            "json": {
                "event": "Test Event",
                "data": {"extra info": "something", "more info": 42},
            }
        },
        {"json": {"event": "Test Event", "user_id": -1, "receiver_id": -1}},
        {"json": {"event": "Test Event", "room_id": -1, "receiver_id": -1}},
        {
            "data": {"event": "Test Event"},
            "headers": {"Content-Type": "application/json"},
        },
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, content, users, rooms):
        # replace placeholder by valid id
        for key in content:
            if content[key].get("room_id") == -1:
                content[key]["room_id"] = rooms.json["id"]
            if content[key].get("user_id") == -1:
                content[key]["user_id"] = users.json["id"]
            if content[key].get("receiver_id") == -1:
                content[key]["receiver_id"] = users.json["id"]
        data = content.get("json", {}) or content.get("data", {})

        # serialize data content to json
        if "data" in content:
            content["data"] = json.dumps(content["data"])

        response = client.post("/slurk/api/logs", **content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        logs = response.json
        assert logs["date_modified"] is None

        # check table specific attributes
        assert logs["event"] == data.get("event")
        assert logs["room_id"] == data.get("room_id", None)
        assert logs["user_id"] == data.get("user_id", None)
        assert logs["receiver_id"] == data.get("receiver_id", None)
        assert logs["data"] == data.get("data", {})


@pytest.mark.depends(on=[f"{PREFIX}::TestRequestOptions::test_request_option[POST]"])
class TestPostInvalid:
    REQUEST_CONTENT = [
        ({"json": {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"event": "Test Event", "data": 42}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"event": "Test Event", "user_id": -42}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, content, status):
        response = client.post("/slurk/api/logs", **content)
        assert response.status_code == status, parse_error(response)

    @pytest.mark.depends(on=["tests/api/test_tokens.py::TestPostValid"])
    def test_unauthorized_access(self, client, tokens):
        response = client.post(
            "/slurk/api/logs",
            headers={"Authorization": f'Bearer {tokens.json["id"]}'},
            json={"event": "Test Event"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client):
        response = client.post(
            "/slurk/api/logs",
            headers={"Authorization": "Bearer invalid_token"},
            json={"event": "Test Event"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetIdValid:
    def test_valid_request(self, client, logs):
        response = client.get(f'/slurk/api/logs/{logs.json["id"]}')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        assert response.json == logs.json

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/logs/{logs.json["id"]}',
            headers={"If-None-Match": response.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetIdInvalid(LogsTable, InvalidTemplate):
    @property
    def request_method(self):
        return "get"

    def json(self, request):
        return {"json": {"event": "Test Event"}}


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_rooms.py::TestPostValid",
    ]
)
class TestPutValid:
    REQUEST_CONTENT = [
        {"json": {"event": "Test Event", "data": {}}},
        {"json": {"event": "Test Event", "room_id": -1}},
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, content, logs, rooms):
        # replace placeholder by valid id
        for key in content:
            if content[key].get("room_id") == -1:
                content[key]["room_id"] = rooms.json["id"]
        data = content.get("json", {}) or content.get("data", {})

        # set the etag
        content.setdefault("headers", {}).update({"If-Match": logs.headers["ETag"]})

        response = client.put(f'/slurk/api/logs/{logs.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_logs = response.json

        # check that a modification was performed
        assert new_logs["id"] == logs.json["id"]
        assert new_logs["date_created"] == logs.json["date_created"]
        assert response.json["date_modified"] is not None
        assert response.headers["ETag"] != logs.headers["ETag"]

        # check table specific attributes
        assert new_logs["event"] == data.get("event")
        assert new_logs["room_id"] == data.get("room_id", None)
        assert new_logs["user_id"] == data.get("user_id", None)
        assert new_logs["receiver_id"] == data.get("receiver_id", None)
        assert new_logs["data"] == data.get("data", {})


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPutInvalid(LogsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "put"

    def json(self, request):
        return {"json": {"event": "Test Event"}}

    REQUEST_CONTENT = [
        ({"json": {"event": None}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"event": "Test Event", "data": ""}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"event": "Test Event", "room_id": -42}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        ({"data": {"event": "Test Event"}}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, logs, content, status):
        # set the etag
        content.setdefault("headers", {}).update({"If-Match": logs.headers["ETag"]})

        response = client.put(f'/slurk/api/logs/{logs.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteValid:
    def test_valid_request(self, client, logs):
        response = client.delete(
            f'/slurk/api/logs/{logs.json["id"]}',
            headers={"If-Match": logs.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteInvalid(LogsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "delete"


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchValid:
    REQUEST_CONTENT = [
        {"json": {"event": "Another Test Event"}},
        {"json": {"user_id": None}},
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, logs, content):
        data = content.get("json", {}) or content.get("data", {})

        # set the etag
        content.setdefault("headers", {}).update({"If-Match": logs.headers["ETag"]})

        response = client.patch(f'/slurk/api/logs/{logs.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_logs = response.json

        # check that a modification was performed
        assert new_logs["id"] == logs.json["id"]
        assert new_logs["date_created"] == logs.json["date_created"]
        assert response.json["date_modified"] is not None
        assert response.headers["ETag"] != logs.headers["ETag"]

        # check table specific attributes
        expected_event = data.get("event", logs.json["event"])
        assert new_logs["event"] == expected_event
        expected_room_id = data.get("room_id", logs.json["room_id"])
        assert new_logs["room_id"] == expected_room_id
        expected_user_id = data.get("user_id", logs.json["user_id"])
        assert new_logs["user_id"] == expected_user_id
        expected_receiver_id = data.get("receiver_id", logs.json["receiver_id"])
        assert new_logs["receiver_id"] == expected_receiver_id
        expected_data = data.get("data", logs.json["data"])
        assert new_logs["data"] == expected_data


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestPatchInvalid(LogsTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "patch"

    REQUEST_CONTENT = [
        ({"json": {"user_id": -42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"data": '{"event": "Test Event"}'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, logs, content, status):
        # set the etag
        content.setdefault("headers", {}).update({"If-Match": logs.headers["ETag"]})

        response = client.patch(f'/slurk/api/logs/{logs.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)
