import json
from collections.abc import Callable, Iterable
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, ValidationError


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


def already_exists_factory(uid: UUID | str = "{UID}", resource_name: str = "Resource"):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{resource_name} {uid} already exists.",
    )


def draft_validation_exception_factory(
    __validation_exception: ValidationError,
    uid: UUID | str = "{UID}",
):
    error = __validation_exception.errors()
    error = {
        "message": f"Failed to validate {repr(__validation_exception.model.__name__)} ({uid}).",
        "errors": error,
    }
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)


AUTHORIZATION_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Provided credentials can't be validated.",
    headers={"WWW-Authenticate": "Bearer"},
)

FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden."
)

NOT_SUPPORTED_SOCIAL_MEDIA_SITE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Not supported third-party social media site.",
)

TOO_MANY_DRAFTS = HTTPException(
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You have too many drafts."
)
