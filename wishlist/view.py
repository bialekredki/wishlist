import re
from collections.abc import Callable, Iterable

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from wishlist.exceptions import exceptions_to_mapping


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
        common_exceptions = getattr(obj, "EXCEPTIONS", {}).get("__all__", tuple())
        for method in dir(obj):
            if method in ("get", "put", "post", "delete"):
                response_model = getattr(obj, "RESPONSE_MODEL", {}).get(method)
                response_class = getattr(obj, "RESPONSE_CLASS", {}).get(
                    method, JSONResponse
                )
                exceptions: Iterable[HTTPException] = getattr(
                    obj, "EXCEPTIONS", {}
                ).get(method, list())
                exceptions += common_exceptions
                router.add_api_route(
                    path,
                    getattr(obj, method),
                    methods=[method],
                    response_class=response_class,
                    response_model=response_model,
                    responses=exceptions_to_mapping(exceptions),
                    name=name_parser(cls, method),
                )

    return _decorator
