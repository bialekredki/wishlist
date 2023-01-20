import asyncio

from httpx import AsyncClient

from tests.utils import access_token_header, assert_http_exception
from wishlist.config import settings
from wishlist.exceptions import TOO_MANY_DRAFTS


async def test_user_can_own_limited_amount_of_drafts(
    test_client: AsyncClient, user_factory, list_draft_factory, list_draft_input_data
):
    user = await user_factory()
    await asyncio.gather(
        *(list_draft_factory(user.id) for _ in range(settings.drafts_max_ammount))
    )
    response = await test_client.get(
        "/me/drafts", headers=access_token_header(user.slug, user.id)
    )
    print(len(response.json()))
    response = await test_client.post(
        "/list/draft",
        headers=access_token_header(user.slug, user.id),
        json=list_draft_input_data,
    )
    assert assert_http_exception(TOO_MANY_DRAFTS, response)
