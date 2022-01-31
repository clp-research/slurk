# -*- coding: utf-8 -*-
"""Test requests to the `tasks` table."""

from http import HTTPStatus
import json
import os

import pytest

from .. import parse_error
from tests.api import InvalidWithEtagTemplate, RequestOptionsTemplate


PREFIX = f'{__name__.replace(".", os.sep)}.py'


class TasksTable:
    @property
    def table_name(self):
        return "tasks"


class TestRequestOptions(TasksTable, RequestOptionsTemplate):
    pass


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetValid:
    def test_valid_request(self, client, tasks):
        response = client.get("/slurk/api/tasks")
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        # check that the posted table instance is included
        def retr_by_id(inst):
            return inst["id"] == tasks.json["id"]

        retr_inst = next(filter(retr_by_id, response.json), None)
        assert retr_inst == tasks.json

        # check that the `get` request did not alter the database
        response = client.get(
            "/slurk/api/tasks", headers={"If-None-Match": response.headers["ETag"]}
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        "tests/api/test_layouts.py::TestPostValid",
    ]
)
class TestPostValid:
    REQUEST_CONTENT = [
        {"json": {"num_users": 3, "name": "Test Task", "layout_id": -1}},
        {"json": {"num_users": "3", "name": "Test Task", "layout_id": -1}},
        {"json": {"num_users": 5, "name": "", "layout_id": -1}},
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, content, layouts):
        # replace placeholder by valid layout id
        for key in content:
            if content[key].get("layout_id") == -1:
                content[key]["layout_id"] = layouts.json["id"]
        data = content.get("json", {}) or content.get("data", {})

        response = client.post("/slurk/api/tasks", **content)
        assert response.status_code == HTTPStatus.CREATED, parse_error(response)

        tasks = response.json
        assert tasks["date_modified"] is None

        # check table specific attributes
        assert tasks["name"] == data.get("name")
        assert tasks["num_users"] == int(data.get("num_users"))
        assert tasks["layout_id"] == data.get("layout_id")


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option[POST]",
        "tests/api/test_layouts.py::TestPostValid",
    ]
)
class TestPostInvalid:
    REQUEST_CONTENT = [
        (
            {"json": {"name": "Test Task", "layout_id": -1}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        ({"json": {"num_users": 3, "layout_id": -1}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"num_users": 3, "name": "Test Task", "layout_id": -42}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"num_users": "drei", "name": "Test Task", "layout_id": -1}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"num_users": 2**63, "name": "Test Task", "layout_id": -1}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"data": {"num_users": 3, "name": "Test Task", "layout_id": -1}},
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        ),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, content, status, layouts):
        # set valid layout id
        for key in content:
            if content[key].get("layout_id") == -1:
                content[key]["layout_id"] = layouts.json["id"]

        response = client.post("/slurk/api/tasks", **content)
        assert response.status_code == status, parse_error(response)

    @pytest.mark.depends(on=["tests/api/test_tokens.py::TestPostValid"])
    def test_unauthorized_access(self, client, tokens, layouts):
        response = client.post(
            "/slurk/api/tasks",
            headers={"Authorization": f'Bearer {tokens.json["id"]}'},
            json={"num_users": 3, "name": "Test Task", "layout_id": layouts.json["id"]},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client, layouts):
        response = client.post(
            "/slurk/api/tasks",
            headers={"Authorization": "Bearer invalid_token"},
            json={"num_users": 3, "name": "Test Task", "layout_id": layouts.json["id"]},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestGetIdValid:
    def test_valid_request(self, client, tasks):
        response = client.get(f'/slurk/api/tasks/{tasks.json["id"]}')
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        assert response.json == tasks.json

        # check that the `get` request did not alter the database
        response = client.get(
            f'/slurk/api/tasks/{tasks.json["id"]}',
            headers={"If-None-Match": response.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NOT_MODIFIED


@pytest.mark.depends(
    on=[f"{PREFIX}::TestRequestOptions::test_request_option_with_id[GET]"]
)
class TestGetIdInvalid:
    def test_not_existing(self, client):
        response = client.get("/slurk/api/tasks/invalid_id")
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_layouts.py::TestPostValid",
    ]
)
class TestPutValid:
    REQUEST_CONTENT = [
        {"json": {"num_users": 0, "name": "", "layout_id": -1}},
        {"json": {"num_users": "5", "name": "äöüß", "layout_id": -1}},
        {
            "data": {"num_users": 5, "name": "Test Task", "layout_id": -1},
            "headers": {"Content-Type": "application/json"},
        },
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, tasks, content, layouts):
        # set valid layout id
        for key in content:
            if content[key].get("layout_id") == -1:
                content[key]["layout_id"] = layouts.json["id"]
        data = content.get("json", {}) or content.get("data", {})

        # serialize data content to json
        if "data" in content:
            content["data"] = json.dumps(content["data"])

        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tasks.headers["ETag"]})

        response = client.put(f'/slurk/api/tasks/{tasks.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_tasks = response.json

        # check that a modification was performed
        assert new_tasks["id"] == tasks.json["id"]
        assert new_tasks["date_created"] == tasks.json["date_created"]
        assert response.json["date_modified"] is not None
        assert response.headers["ETag"] != tasks.headers["ETag"]

        assert new_tasks["date_created"] == tasks.json["date_created"]
        assert new_tasks["id"] == tasks.json["id"]
        assert new_tasks["name"] == data.get("name")
        assert new_tasks["num_users"] == int(data.get("num_users"))
        assert new_tasks["layout_id"] == data.get("layout_id")


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PUT]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_layouts.py::TestPostValid",
    ]
)
class TestPutInvalid(TasksTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "put"

    def json(self, request):
        layouts = request.getfixturevalue("layouts")
        return {
            "json": {
                "num_users": 3,
                "name": "Test Task",
                "layout_id": layouts.json["id"],
            }
        }

    REQUEST_CONTENT = [
        ({"json": {}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"json": {"num_users": 3, "name": "Test Task"}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"num_users": 3, "name": None, "layout_id": -1}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"num_users": None, "name": "Test Task", "layout_id": -1}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            {"json": {"num_users": -2, "name": "Test Task", "layout_id": -1}},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, tasks, content, status, layouts):
        # set valid layout id
        for key in content:
            if content[key].get("layout_id") == -1:
                content[key]["layout_id"] = layouts.json["id"]
        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tasks.headers["ETag"]})

        response = client.put(f'/slurk/api/tasks/{tasks.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteValid:
    def test_valid_request(self, client, tasks):
        response = client.delete(
            f'/slurk/api/tasks/{tasks.json["id"]}',
            headers={"If-Match": tasks.headers["ETag"]},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[DELETE]",
        f"{PREFIX}::TestPostValid",
    ]
)
class TestDeleteInvalid(TasksTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "delete"

    @pytest.mark.depends(
        on=[
            "tests/api/test_tokens.py::TestPostValid",
            "tests/api/test_tokens.py::TestDeleteValid",
        ]
    )
    def test_deletion_of_task_in_token(self, client, permissions, tasks):
        # create token that uses the task
        token = client.post(
            "/slurk/api/tokens",
            json={
                "permissions_id": permissions.json["id"],
                "task_id": tasks.json["id"],
            },
        )
        # the deletion of a tasks entry that is in use should fail
        response = client.delete(
            f'/slurk/api/tasks/{tasks.json["id"]}',
            headers={"If-Match": tasks.headers["ETag"]},
        )
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # , parse_error(response)

        # free the task entry by deleting the token
        response = client.delete(
            f'/slurk/api/tokens/{token.json["id"]}',
            headers={"If-Match": token.headers["ETag"]},
        )
        # now one should be able to delete the task
        response = client.delete(
            f'/slurk/api/tasks/{tasks.json["id"]}',
            headers={"If-Match": tasks.headers["ETag"]},
        )

        assert response.status_code == HTTPStatus.NO_CONTENT, parse_error(response)


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_layouts.py::TestPostValid",
    ]
)
class TestPatchValid:
    REQUEST_CONTENT = [
        {"json": {"num_users": 0, "layout_id": -1}},
        {"json": {"name": "Another Task", "layout_id": -1}},
        {
            "data": {"num_users": 2, "layout_id": -1},
            "headers": {"Content-Type": "application/json"},
        },
    ]

    @pytest.mark.parametrize("content", REQUEST_CONTENT)
    def test_valid_request(self, client, tasks, content, layouts):
        # set valid layout id
        for key in content:
            if content[key].get("layout_id") == -1:
                content[key]["layout_id"] = layouts.json["id"]
        data = content.get("json", {}) or content.get("data", {})

        # serialize data content to json
        if "data" in content:
            content["data"] = json.dumps(content["data"])

        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tasks.headers["ETag"]})

        response = client.patch(f'/slurk/api/tasks/{tasks.json["id"]}', **content)
        assert response.status_code == HTTPStatus.OK, parse_error(response)

        new_tasks = response.json

        # check that a modification was performed
        assert new_tasks["id"] == tasks.json["id"]
        assert new_tasks["date_created"] == tasks.json["date_created"]
        assert response.json["date_modified"] is not None
        assert response.headers["ETag"] != tasks.headers["ETag"]

        expected_name = data.get("name", tasks.json["name"])
        assert new_tasks["name"] == expected_name
        expected_num_users = data.get("num_users", tasks.json["num_users"])
        assert new_tasks["num_users"] == expected_num_users
        expected_layout = data.get("layout_id", tasks.json["layout_id"])
        assert new_tasks["layout_id"] == expected_layout


@pytest.mark.depends(
    on=[
        f"{PREFIX}::TestRequestOptions::test_request_option_with_id[PATCH]",
        f"{PREFIX}::TestPostValid",
        "tests/api/test_layouts.py::TestPostValid",
    ]
)
class TestPatchInvalid(TasksTable, InvalidWithEtagTemplate):
    @property
    def request_method(self):
        return "patch"

    REQUEST_CONTENT = [
        ({"json": {"id": 2}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"layout_id": -42}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"json": {"num_users": -1}}, HTTPStatus.UNPROCESSABLE_ENTITY),
        (
            {"data": {"name": "Another Test Room", "layout_id": -1}},
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        ),
        ({"data": '{"name": "Another Test Room"}'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE),
    ]

    @pytest.mark.parametrize("content, status", REQUEST_CONTENT)
    def test_invalid_request(self, client, tasks, content, status, layouts):
        # set valid layout id
        for key in content:
            if isinstance(content[key], dict) and content[key].get("layout_id") == -1:
                content[key]["layout_id"] = layouts.json["id"]
        # set the etag
        content.setdefault("headers", {}).update({"If-Match": tasks.headers["ETag"]})

        response = client.patch(f'/slurk/api/tasks/{tasks.json["id"]}', **content)
        assert response.status_code == status, parse_error(response)
