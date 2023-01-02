import logging
from collections.abc import Iterable
from typing import Any, ClassVar

import bcrypt
from edgedb.errors import ConstraintViolationError
from fastapi import APIRouter, Query
from slugify import slugify

import wishlist.exceptions as exceptions
import wishlist.query as dbquery
from wishlist.database import client
from wishlist.schemas.user import CreateUser, DetailedUser, PublicUser
from wishlist.view import view

router = APIRouter()
logger = logging.getLogger("users-endpoints")


@router.get("/users", response_model=Iterable[PublicUser])
async def search_users(query: str = Query(None, max_length=128, alias="q")):
    if query:
        users = await dbquery.get_users_by_name(client, name=query)
    else:
        users = await dbquery.get_users(client)
    return users


@view(router, path="/user")
class UserView:

    RESPONSE_MODEL: ClassVar[dict[str, Any]] = {"post": PublicUser, "get": DetailedUser}
    EXCEPETIONS: ClassVar[dict[str, Any]] = {
        "post": (exceptions.already_exists_factory,)
    }

    async def get(self, slug: str = Query(..., max_length=128)):
        """Get User"""
        user = await dbquery.get_user_detailed(client, slug=slug)
        if len(user) != 1:
            raise exceptions.not_found_exception_factory(slug)
        return user[0]

    async def post(self, data: CreateUser):
        """Create user"""
        password_hash = bcrypt.hashpw(
            data.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        slug = slugify(data.name, max_length=100)
        nslug = slug
        for iter in range(2**10):
            user = await dbquery.get_user_by_slug(client, slug=nslug)
            if not user:
                break
            nslug = f"{slug}#{iter:x}"
        try:
            created_user = await dbquery.create_user(
                client,
                name=data.name,
                email=data.email,
                slug=nslug,
                password_hash=password_hash,
            )
        except ConstraintViolationError:
            raise exceptions.already_exists_factory(data.email)
        return created_user
