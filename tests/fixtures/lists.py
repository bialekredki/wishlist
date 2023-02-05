import pytest
from nanoid import generate

from wishlist.query import create_list

from tests.utils import ALPHANUMERIC_ALPHABET


@pytest.fixture(name="wishlist_data")
def fixture_wishlist_data():
    return {"thumbnail": "test", "description": "none", "name": "test"}


@pytest.fixture
def wishlist_factory(client, list_draft_factory, wishlist_data):
    async def _factory(uid, data: dict | None = None, with_draft=False):
        data = data or wishlist_data
        slug = f"{data['name']}-{generate(alphabet=ALPHANUMERIC_ALPHABET, size=5)}"
        _list = await create_list(
            client,
            name=data["name"],
            thumbnail=data.get("thumbnail"),
            description=data.get("description"),
            slug=slug,
            uid=uid,
        )
        if with_draft:
            draft_data = dict(name=data["name"], draft={"draft_items": []})
            for key in ("thumbnail", "description"):
                if key in data and key is not None:
                    draft_data["draft"][key] = data[key]
            list_draft = await list_draft_factory(
                uid, data=draft_data, active_list_slug=slug
            )
            return _list, list_draft
        return _list

    return _factory
