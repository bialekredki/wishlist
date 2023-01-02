from collections.abc import Callable, Iterable
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class __ExceptionModel(BaseModel):
    detail: str = Field(..., description="Exception details.")


def exceptions_to_mapping(
    exceptions: Iterable[HTTPException | Callable[..., HTTPException]]
):
    mapping = {}
    for exception in exceptions:
        exc = exception if isinstance(exception, HTTPException) else exception()
        if exc.status_code not in mapping:
            mapping[exc.status_code] = {
                "description": exc.detail,
                "model": __ExceptionModel,
            }
        else:
            mapping[exc.status_code]["description"] += f" or {exc.detail}"
    return mapping


def not_found_exception_factory(uid: UUID | str | None = None):
    uid = uid or None
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Can't find {uid}"
    )


def already_exists_factory(uid: UUID | str | None = None):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail=f"{uid} already exists."
    )


AUTHORIZATION_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Provided credentials can't be validated.",
    headers={"WWW-Authenticate": "Bearer"},
)

REQUIRE_HTTPS_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="URL is required to be HTTPS."
)

NOT_SUPPORTED_SOCIAL_MEDIA_SITE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Not supported third-party social media site.",
)
