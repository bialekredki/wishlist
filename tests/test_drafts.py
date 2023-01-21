import asyncio
import json

from fastapi import status
from httpx import AsyncClient

from tests.utils import access_token_header, assert_http_exception
from wishlist import query
from wishlist.config import settings
from wishlist.endpoints.list import ALLOWED_ITEM_DRAFT_FIELDS, ALLOWED_LIST_DRAFT_FIELDS
from wishlist.exceptions import TOO_MANY_DRAFTS


async def test_user_can_own_limited_amount_of_drafts(
    test_client: AsyncClient, user_factory, list_draft_factory, list_draft_input_data
):
    user = await user_factory()
    await asyncio.gather(
        *(list_draft_factory(user.id) for _ in range(settings.drafts_max_ammount))
    )
    response = await test_client.post(
        "/list/draft",
        headers=access_token_header(user.slug, user.id),
        json=list_draft_input_data,
    )
    assert assert_http_exception(TOO_MANY_DRAFTS, response)


async def test_creating_draft__success(
    test_client: AsyncClient, user_factory, list_draft_input_data, client
):
    user = await user_factory()
    response = await test_client.post(
        "/list/draft",
        headers=access_token_header(user.slug, user.id),
        json=list_draft_input_data,
    )
    assert response.status_code == status.HTTP_200_OK
    list_draft = await query.get_draft_owned_by_user(
        client, uid=user.id, id=response.json()["id"]
    )
    assert list_draft
    assert list_draft.name == list_draft_input_data["name"]
    assert json.loads(list_draft.draft) == {
        key: value
        for key, value in list_draft_input_data["draft"].items()
        if key in ALLOWED_LIST_DRAFT_FIELDS
    }
    assert len(list_draft.draft_items) == len(
        list_draft_input_data["draft"]["draft_items"]
    )


async def test_creating_draft__with_name_only(
    test_client: AsyncClient, user_factory, list_draft_input_data
):
    user = await user_factory()
    list_draft_input_data["draft"] = {}
    response = await test_client.post(
        "/list/draft",
        headers=access_token_header(user.slug, user.id),
        json=list_draft_input_data,
    )
    assert response.status_code == status.HTTP_200_OK


async def test_creating_draft__with_unallowed_fields(
    test_client: AsyncClient, user_factory, list_draft_input_data
):
    user = await user_factory()
    list_draft_input_data["draft"]["fake_field"] = "fake_value"
    response = await test_client.post(
        "/list/draft",
        headers=access_token_header(user.slug, user.id),
        json=list_draft_input_data,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["draft"].get("fake_field") is None


async def test_creating_draft__without_draft_items(
    test_client: AsyncClient, user_factory, list_draft_input_data
):
    user = await user_factory()
    list_draft_input_data["draft"]["draft_items"] = []
    response = await test_client.post(
        "/list/draft",
        headers=access_token_header(user.slug, user.id),
        json=list_draft_input_data,
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert not content["draft_items"]


async def test_deleting_drafts(
    test_client: AsyncClient, user_factory, list_draft_factory, client
):
    user = await user_factory()
    list_draft = await list_draft_factory(user.id)
    response = await test_client.request(
        "DELETE",
        "/list/draft",
        json={"id": str(list_draft.id)},
        headers=access_token_header(user.slug, user.id),
    )
    assert response.status_code == status.HTTP_200_OK
    draft_items = await asyncio.gather(
        *(
            query.get_draft_item(client, id=draft_item.id)
            for draft_item in list_draft.draft_items
        )
    )
    assert all(draft_item is None for draft_item in draft_items)
    assert not await query.get_draft_owned_by_user(
        client, uid=user.id, id=list_draft.id
    )
