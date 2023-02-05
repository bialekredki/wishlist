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
    not_found_exception_factory,
)


async def test_user_can_own_limited_amount_of_drafts(
    test_client: AsyncClient, user_factory, list_draft_factory, list_draft_input_data
):
    user = await user_factory()
    await asyncio.gather(
        *(list_draft_factory(user.id) for _ in range(settings.drafts_max_ammount))
    )
    response = await test_client.post(
        "/draft/list",
        headers=access_token_header(user.slug, user.id),
        json=list_draft_input_data,
    )
    assert assert_http_exception(TOO_MANY_DRAFTS, response)


async def test_creating_draft__success(
    test_client: AsyncClient, user_factory, list_draft_input_data, client
):
    user = await user_factory()
    response = await test_client.post(
        "/draft/list",
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
        "/draft/list",
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
        "/draft/list",
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
        "/draft/list",
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
        "/draft/list",
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


async def test_getting_draft_items(
    test_client: AsyncClient, user_factory, list_draft_factory, list_draft_input_data
):
    user = await user_factory()
    list_draft = await list_draft_factory(user.id)
    response = await test_client.get(
        "/item/draft",
        params={"id": list_draft.draft_items[0].id},
        headers=access_token_header(user.slug, user.id),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["draft"] == {
        key: value
        for key, value in list_draft_input_data["draft"]["draft_items"][0].items()
        if key != "name"
    }


@pytest.mark.parametrize("http_method", ("GET", "DELETE"))
async def test_accessing_someone_else_draft_item(
    test_client: AsyncClient, user_factory, list_draft_factory, http_method
):
    owner = await user_factory()
    bystander = await user_factory()
    list_draft = await list_draft_factory(owner.id)
    params = {"id": list_draft.draft_items[0].id} if http_method == "GET" else None
    body = {"id": str(list_draft.draft_items[0].id)} if http_method != "GET" else None
    response = await test_client.request(
        http_method,
        "/item/draft",
        params=params,
        json=body,
        headers=access_token_header(bystander.slug, bystander.id),
    )
    assert_http_exception(FORBIDDEN_EXCEPTION, response)


async def test_creating_draft_item(
    user_factory, draft_input_data, list_draft_factory, client
):
    user: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(user.id)
    response = await user.post(
        "/item/draft",
        json={
            "list_id": str(list_draft.id),
            "draft": draft_input_data,
            "name": draft_input_data["name"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["id"]
    draft = await query.get_draft_item(client, id=content["id"])
    assert draft is not None
    assert draft.list_draft.owner.id == user.id


async def test_creating_draft_item__unwanted_fields(
    user_factory, draft_input_data, list_draft_factory
):
    user: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(user.id)
    draft_input_data["unwanted_field"] = "unwanted_data"
    response = await user.post(
        "/item/draft",
        json={
            "list_id": str(list_draft.id),
            "draft": draft_input_data,
            "name": draft_input_data["name"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["draft"]
    assert "unwanted_field" not in content["draft"]


async def test_creating_draft_item__flat_draft_structure(
    user_factory, draft_input_data, list_draft_factory
):
    user: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(user.id)
    draft_input_data["count"] = {"value": 25}

    response = await user.post(
        "/item/draft",
        json={"list_id": str(list_draft.id), "draft": draft_input_data, "name": "test"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["draft"]
    assert "count" not in content["draft"]


async def test_deleting_draft_item(
    user_factory, list_draft_factory, draft_item_factory, client
):
    user: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(user.id)
    draft_item = await draft_item_factory(list_draft.id)

    response = await user.delete("/item/draft", json={"id": str(draft_item.id)})

    assert response.status_code == status.HTTP_200_OK
    result = await query.get_draft_item(client, id=draft_item.id)
    assert result is None


async def test_list_draft_update(user_factory, list_draft_factory):
    user: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(user.id)

    response = await user.patch(
        f"/draft/list/{str(list_draft.id)}",
        json={
            "draft": {"thumbnail": "thumbnail of renamed draft"},
            "name": "Renamed Draft",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["name"] == "Renamed Draft"
    assert content["draft"]["thumbnail"] == "thumbnail of renamed draft"
    assert datetime.fromisoformat(content["last_edit_at"]) > list_draft.last_edit_at


async def test_list_draft_update__other_user(user_factory, list_draft_factory):
    owner = await user_factory()
    bystander: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(owner.id)
    response = await bystander.patch(
        f"/draft/list/{list_draft.id}", json={"name": "name", "draft": {"test": "test"}}
    )
    assert_http_exception(not_found_exception_factory, response)


async def test_item_draft_update(user_factory, list_draft_factory, draft_item_factory):
    user: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(user.id)
    draft_item = await draft_item_factory(list_draft.id)
    response = await user.patch(
        f"/item/draft/{str(draft_item.id)}",
        json={
            "draft": {"thumbnail": "thumbnail of renamed draft"},
            "name": "Renamed Draft",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["name"] == "Renamed Draft"
    assert content["draft"]["thumbnail"] == "thumbnail of renamed draft"
    assert datetime.fromisoformat(content["last_edit_at"]) > list_draft.last_edit_at


async def test_item_draft_update__other_user(
    user_factory, list_draft_factory, draft_item_factory
):
    owner = await user_factory()
    bystander: UserWithTestClient = await user_factory()
    list_draft = await list_draft_factory(owner.id)
    draft_item = await draft_item_factory(list_draft.id)
    response = await bystander.patch(
        f"/item/draft/{draft_item.id}", json={"name": "name", "draft": {"test": "test"}}
    )
    assert_http_exception(FORBIDDEN_EXCEPTION, response)
