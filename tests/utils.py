import json
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

from fastapi import HTTPException
from httpx import AsyncClient, Response

from wishlist.security import create_access_token

ALPHANUMERIC_ALPHABET = "1234567890QWERTYUOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"


class Rollback(Exception):
    ...


def assert_http_exception(exception: HTTPException | Callable, response: Response):
    if callable(exception):
        exception = exception()
    assert isinstance(
        exception, HTTPException
    ), f"Expected HTTPException, found {type(exception)}"
    assert (
        exception.status_code == response.status_code
    ), f"Expected {exception.status_code}, got {response.status_code}({response.json()})"
    return True


def access_token_header(slug: str, uid: UUID):
    return {
        "Authorization": "Bearer "
        + create_access_token(dict(sub=json.dumps(dict(slug=slug, id=str(uid)))))
    }


@dataclass(init=True)
class UserWithTestClient:
    test_client: AsyncClient
    slug: str
    id: UUID
    slug: str
    email: str
    name: str

    def make_request_headers(self, headers: dict | None):
        authorization_header = access_token_header(self.slug, self.id)
        headers = headers or {}
        headers.update(authorization_header)
        return headers

    async def get(
        self, url, *, params: dict | None = None, headers: dict | None = None
    ) -> Response:
        return await self.test_client.get(
            url, params=params, headers=self.make_request_headers(headers)
        )

    async def post(self, url, *, json: dict | None = None, headers: dict | None = None):
        return await self.test_client.post(
            url, json=json, headers=self.make_request_headers(headers)
        )

    async def delete(
        self, url, *, json: dict | None = None, headers: dict | None = None
    ):
        return await self.test_client.request(
            "DELETE", url, json=json, headers=self.make_request_headers(headers)
        )

    async def patch(
        self, url, *, json: dict | None = None, headers: dict | None = None
    ):
        return await self.test_client.patch(
            url, json=json, headers=self.make_request_headers(headers)
        )
