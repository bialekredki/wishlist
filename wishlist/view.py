import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from functools import wraps

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from wishlist.exceptions import exceptions_to_mapping


class Method(str, Enum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"
    PUT = "put"


@dataclass(frozen=True, init=True, repr=True)
class EndpointMetadata:
    methods: set[Method]
    name: str | None = None
    path: str | None = None


def _view_class_name_default_parser(cls, method: str):
    class_name = " ".join(re.findall(r"[A-Z][^A-Z]*", cls.__name__.replace("View", "")))
    return method.capitalize() + " " + class_name


def view(
    router: FastAPI | APIRouter,
    *,
    path: str = "/",
    name_parser: Callable[..., str] = _view_class_name_default_parser,
):
    def _decorator(cls) -> None:
        obj = cls()
        cls_based_response_model = getattr(obj, "RESPONSE_MODEL", {})
        cls_based_response_class = getattr(obj, "RESPONSE_CLASS", {})
        common_exceptions = getattr(obj, "EXCEPTIONS", {}).get("__all__", tuple())
        for _callable_name in dir(obj):
            _callable = getattr(obj, _callable_name)
            if _callable_name in ("get", "put", "post", "delete", "patch") or hasattr(
                _callable, "__endpoint_metadata"
            ):
                metadata: EndpointMetadata | None = getattr(
                    _callable, "__endpoint_metadata", None
                )
                response_model = cls_based_response_model.get(_callable_name)
                response_class = cls_based_response_class.get(
                    _callable_name, JSONResponse
                )
                exceptions: Iterable[HTTPException] = getattr(
                    obj, "EXCEPTIONS", {}
                ).get(_callable_name, [])
                exceptions += common_exceptions
                method = list(metadata.methods) if metadata else [_callable_name]
                name = (
                    metadata.name
                    if metadata and metadata.name
                    else name_parser(cls, _callable_name)
                )
                _path = path
                if metadata and metadata.path:
                    _path = path + metadata.path
                router.add_api_route(
                    _path,
                    _callable,
                    methods=method,
                    response_class=response_class,
                    response_model=response_model,
                    responses=exceptions_to_mapping(exceptions),
                    name=name,
                )

    return _decorator


def endpoint(
    methods: Iterable[str | Method] | None = None,
    *,
    name: str | None = None,
    path: str | None = None,
):
    def _decorator(function: Callable):
        @wraps(function)
        async def _wrapper(*args, **kwargs):
            return await function(*args, **kwargs)

        parsed_methods = set()
        _methods = methods or ((name,) if name else (function.__name__,))
        for method in _methods:
            if isinstance(method, Method):
                parsed_methods.add(method)
                continue
            try:
                parsed_methods.add(Method[method.upper()])
            except KeyError:
                raise ValueError(f"HTTP Method {method} is not allowed")

        metadata = EndpointMetadata(name=name, methods=parsed_methods, path=path)
        _wrapper.__endpoint_metadata = metadata
        return _wrapper

    return _decorator
