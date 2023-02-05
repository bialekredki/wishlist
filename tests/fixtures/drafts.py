import asyncio
import copy
import json

import pytest

from wishlist import query


@pytest.fixture(name="draft_input_data")
def fixture_draft_input_data():
    return {
        "thumbnail": "test",
        "description": "none",
        "price": None,
        "name": "Test Item Draft",
        "count": 5,
        "min_price": 0,
        "max_price": 150,
    }


@pytest.fixture(name="list_draft_input_data")
def fixture_list_draft_input_data(draft_input_data):
    draft_item = copy.deepcopy(draft_input_data)
    return {
        "name": "Test List Draft",
        "draft": {
            "thumbnail": "test",
            "description": "no",
            "draft_items": [draft_item],
        },
    }


@pytest.fixture
def list_draft_data_factory(list_draft_input_data):
    def _factory(input_data):
        data = copy.deepcopy(list_draft_input_data)
        data.update(input_data)
        return data

    return _factory


@pytest.fixture
def draft_item_factory(client, transaction, draft_input_data):
    async def _factory(list_id, data=None):
        data = data or draft_input_data
        return await query.create_list_item_draft(
            client,
            name=data["name"],
            draft=json.dumps(
                {key: value for key, value in data.items() if key != "name"}
            ),
            list_id=list_id,
        )

    return _factory


@pytest.fixture
def list_draft_factory(client, transaction, list_draft_input_data):
    async def _factory(uid, data=None):
        data = data or list_draft_input_data
        result = await query.create_list_draft(
            client,
            uid=uid,
            name=data["name"],
            list_slug=None,
            draft=json.dumps(
                {
                    key: value
                    for key, value in data["draft"].items()
                    if key in ("thumbnail", "description")
                }
            ),
        )
        draft_items = await asyncio.gather(
            *(
                query.create_list_item_draft(
                    client,
                    name=draft_item["name"],
                    draft=json.dumps(
                        {
                            key: value
                            for key, value in draft_item.items()
                            if key
                            in (
                                "thumbnail",
                                "description",
                                "price",
                                "count",
                                "url",
                                "max_price",
                                "min_price",
                            )
                        }
                    ),
                    list_id=result.id,
                )
                for draft_item in data["draft"].get("draft_items", [])
            )
        )
        return await query.get_draft_owned_by_user(client, uid=uid, id=result.id)

    return _factory
