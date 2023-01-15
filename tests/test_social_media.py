from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.utils import access_token_header, assert_http_exception
from wishlist.exceptions import NOT_SUPPORTED_SOCIAL_MEDIA_SITE
from wishlist.query import get_user_social_media


async def test_listing_allowed_social_media_sites(
    test_client: AsyncClient, allowed_social_media_site
):
    response = await test_client.get("/metadata/allowed_social_media_sites")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert isinstance(content, list)
    assert len(content) == 1


@pytest.mark.parametrize("protocol", ("http", "https"))
async def test_link_social_media_site__only_https(
    test_client: AsyncClient,
    user_factory,
    client,
    allowed_social_media_site,
    faker,
    protocol,
):
    user = await user_factory()
    response = await test_client.post(
        "/me/social_media",
        headers=access_token_header(user.slug, user.id),
        json={
            "url": f"{protocol}://{allowed_social_media_site.domain}/{faker.user_name()}"
        },
    )
    assert (
        response.status_code == status.HTTP_200_OK
        if protocol == "https"
        else status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    social_media = await get_user_social_media(client, id=user.id)
    assert social_media
    assert len(social_media.third_party_social_media) == (
        1 if protocol == "https" else 0
    )


async def test_link_social_media_site__unallowed(
    test_client: AsyncClient, faker, user_factory
):
    user = await user_factory()
    response = await test_client.post(
        "/me/social_media",
        headers=access_token_header(user.slug, user.id),
        json={"url": f"https://test.com/{faker.user_name()}"},
    )
    assert_http_exception(NOT_SUPPORTED_SOCIAL_MEDIA_SITE, response)


async def test_list_linked_social_media(
    test_client: AsyncClient,
    user_factory,
    user_social_media_factory,
    allowed_social_media_site,
    faker,
):
    user = await user_factory()
    user_social_media = await user_social_media_factory(
        name=allowed_social_media_site.name,
        url=f"https://{allowed_social_media_site.domain}/{faker.user_name()}",
        user_id=user.id,
    )
    response = await test_client.get(
        "/me/social_media", headers=access_token_header(user.slug, user.id)
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content["third_party_social_media"]) == 1


async def test_unlink_social_media(
    test_client: AsyncClient,
    user_factory,
    user_social_media_factory,
    allowed_social_media_site,
    faker,
    client,
):
    user = await user_factory()
    user_social_media = (
        await user_social_media_factory(
            name=allowed_social_media_site.name,
            url=f"https://{allowed_social_media_site.domain}/{faker.user_name()}",
            user_id=user.id,
        )
    ).third_party_social_media[0]
    response = await test_client.request(
        "DELETE",
        "/me/social_media",
        headers=access_token_header(user.slug, user.id),
        json={"id": str(user_social_media.id)},
    )
    assert response.status_code == status.HTTP_200_OK
    query_result = await get_user_social_media(client, id=user.id)
    assert query_result
    assert len(query_result.third_party_social_media) == 0


async def test_unlink_social_media__not_found(test_client: AsyncClient, user_factory):
    user = await user_factory()
    response = await test_client.request(
        "DELETE",
        "/me/social_media",
        headers=access_token_header(user.slug, user.id),
        json={"id": str(uuid4())},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_unlink_social_media__not_owned_by_user(
    test_client: AsyncClient,
    user_factory,
    user_social_media_factory,
    allowed_social_media_site,
    faker,
):
    user_1 = await user_factory()
    user_2 = await user_factory()
    social_media = (
        await user_social_media_factory(
            name=allowed_social_media_site.name,
            url=f"https://{allowed_social_media_site.domain}/{faker.user_name()}",
            user_id=user_1.id,
        )
    ).third_party_social_media[0]
    response = await test_client.request(
        "DELETE",
        "/me/social_media",
        headers=access_token_header(user_2.slug, user_2.id),
        json={"id": str(social_media.id)},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
