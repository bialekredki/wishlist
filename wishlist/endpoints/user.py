import logging
from typing import Any, ClassVar

import bcrypt
from edgedb.errors import ConstraintViolationError
from fastapi import APIRouter, Depends, Query
from slugify import slugify

import wishlist.exceptions as exceptions
import wishlist.query as dbquery
from wishlist.database import get_client
from wishlist.schemas.user import CreateUser, DetailedUser, PublicUser
from wishlist.utils.slug import find_unqiue_slug
from wishlist.view import view

router = APIRouter()
logger = logging.getLogger("users-endpoints")


@router.get("/users", response_model=list[PublicUser])
async def search_users(
    query: str = Query(None, max_length=128, alias="q", description="Search query."),
    client=Depends(get_client),
):
    if query:
        users = await dbquery.get_users_by_name(client, name=query)
    else:
        users = await dbquery.get_users(client)
    return users


@view(router, path="/user")
class UserView:

    RESPONSE_MODEL: ClassVar[dict[str, Any]] = {"post": PublicUser, "get": DetailedUser}
    EXCEPTIONS: ClassVar[dict[str, Any]] = {
        "post": (exceptions.already_exists_factory,)
    }

    async def get(
        self,
        slug: str = Query(..., max_length=128),
        client=Depends(get_client),
    ):
        """Get User"""
        user = await dbquery.get_user_detailed(client, slug=slug)
        if len(user) != 1:
            raise exceptions.not_found_exception_factory(slug)
        return user[0]

    async def post(
        self,
        data: CreateUser,
        client=Depends(get_client),
    ):
        """Create user"""
        password_hash = bcrypt.hashpw(
            data.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        for _ in range(2**5):
            slug = await find_unqiue_slug(data.name, dbquery.get_user_by_slug)
            try:
                return await dbquery.create_user(
                    client,
                    name=data.name,
                    email=data.email,
                    slug=slug,
                    password_hash=password_hash,
                )
            except ConstraintViolationError as exc:
                if "email" in str(exc):
                    break
        raise exceptions.already_exists_factory(data.email, "User")
