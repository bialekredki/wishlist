import asyncio
import json
from datetime import datetime

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.utils import UserWithTestClient, access_token_header, assert_http_exception
from wishlist import query
from wishlist.config import settings
from wishlist.endpoints.list import ALLOWED_ITEM_DRAFT_FIELDS, ALLOWED_LIST_DRAFT_FIELDS
from wishlist.exceptions import (
    FORBIDDEN_EXCEPTION,
    TOO_MANY_DRAFTS,
    already_exists_factory,
)


async def test_user_cant_redraft_list_if_over_limit(
    user_factory, list_draft_factory, wishlist_factory
):
    user: UserWithTestClient = await user_factory()
    await asyncio.gather(
        *(list_draft_factory(user.id) for _ in range(settings.drafts_max_ammount))
    )
    _list = await wishlist_factory(user.id)
    response = await user.post(f"/list/{_list.slug}")
    assert assert_http_exception(TOO_MANY_DRAFTS, response)


async def test_user_cant_redraft_list_if_already_redrafted(
    user_factory, wishlist_factory
):
    user: UserWithTestClient = await user_factory()
    _list, _ = await wishlist_factory(user.id, with_draft=True)
    response = await user.post(f"/list/{_list.slug}")
    assert assert_http_exception(already_exists_factory, response)


async def test_redraft__succes(user_factory, wishlist_factory):
    user: UserWithTestClient = await user_factory()
    _list = await wishlist_factory(user.id)
    response = await user.post(f"/list/{_list.slug}")
    assert response.status_code == status.HTTP_200_OK
