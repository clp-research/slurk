# -*- coding: utf-8 -*-
"""Template class with tests for insuccessful ressource access."""

from abc import ABC, abstractmethod
from http import HTTPStatus

import pytest

from .. import parse_error


class Template(ABC):
    @property
    @abstractmethod
    def table_name(self):
        """String matching at the same time a table and fixture."""
        pass


class RequestOptionsTemplate(Template):
    @pytest.mark.parametrize("option", ["OPTIONS", "GET", "POST"])
    def test_request_option(self, client, option):
        response = client.options(f"/slurk/api/{self.table_name}")
        if option == "OPTIONS":
            assert response.status_code == HTTPStatus.OK
        # request can only be verified, if the `options` request succeeds
        # if it fails the verification step is left out
        if response.status_code == HTTPStatus.OK:
            assert (
                option in response.headers["Allow"]
            ), HTTPStatus.METHOD_NOT_ALLOWED.description

    @pytest.mark.parametrize("option", ["OPTIONS", "GET", "PUT", "DELETE", "PATCH"])
    def test_request_option_with_id(self, client, request, option):
        table_inst = request.getfixturevalue(self.table_name)
        if table_inst is None:
            pytest.skip(
                f"Depends on tests/api/test_{self.table_name}.py::TestPostValid"
            )
        response = client.options(
            f'/slurk/api/{self.table_name}/{table_inst.json["id"]}'
        )
        if option == "OPTIONS":
            assert response.status_code == HTTPStatus.OK
        if response.status_code == HTTPStatus.OK:
            assert (
                option in response.headers["Allow"]
            ), HTTPStatus.METHOD_NOT_ALLOWED.description


class InvalidTemplate(Template):
    @property
    @abstractmethod
    def request_method(self):
        """Name of request method as lowercase string."""
        pass

    @property
    def url_extension(self):
        """Any suffix appended to `/slurk/api/{table_name}/{id}`"""
        return ""

    def json(self, request):
        """Required arguments if any for the specified method."""
        return {}

    def test_not_existing(self, client, request):
        response = getattr(client, self.request_method)(
            f"/slurk/api/{self.table_name}/invalid_id{self.url_extension}",
            **self.json(request),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, parse_error(response)

    @pytest.mark.depends(on=["tests/api/test_tokens.py::TestPostValid"])
    def test_unauthorized_access(self, client, tokens, request):
        table_inst = request.getfixturevalue(self.table_name)
        response = getattr(client, self.request_method)(
            f'/slurk/api/{self.table_name}/{table_inst.json["id"]}{self.url_extension}',
            **self.json(request),
            headers={
                "Authorization": f'Bearer {tokens.json["id"]}',
                "If-Match": table_inst.headers["ETag"],
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)

    def test_unauthenticated_access(self, client, request):
        table_inst = request.getfixturevalue(self.table_name)
        response = getattr(client, self.request_method)(
            f'/slurk/api/{self.table_name}/{table_inst.json["id"]}{self.url_extension}',
            **self.json(request),
            headers={
                "Authorization": "Bearer invalid_token",
                "If-Match": table_inst.headers["ETag"],
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, parse_error(response)


class InvalidWithEtagTemplate(InvalidTemplate):
    @pytest.mark.parametrize(
        "content, status",
        [
            ({"headers": {"If-Match": "invalid_etag"}}, HTTPStatus.PRECONDITION_FAILED),
            ({}, HTTPStatus.PRECONDITION_REQUIRED),
        ],
    )
    def test_if_match(self, client, request, content, status):
        # create instance of table by calling fixture of the same name
        table_inst = request.getfixturevalue(self.table_name)

        response = getattr(client, self.request_method)(
            f'/slurk/api/{self.table_name}/{table_inst.json["id"]}{self.url_extension}',
            **self.json(request),
            **content,
        )
        assert response.status_code == status, parse_error(response)
