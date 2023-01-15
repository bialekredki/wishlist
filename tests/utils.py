import json
from typing import Callable
from uuid import UUID

from fastapi import HTTPException
from httpx import Response

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
