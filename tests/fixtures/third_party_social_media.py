from uuid import UUID

import pytest

from wishlist.query import create_allowed_social_media, create_user_social_media


@pytest.fixture
def allowed_social_media_factory(client, faker):
    async def _factory(*, name: str | None = None, domain: str | None = None):
        name = name or faker.domain_word()
        domain = domain or name + ".com"
        return await create_allowed_social_media(client, name=name, domain=domain)

    return _factory


@pytest.fixture
def user_social_media_factory(client):
    async def _factory(*, name: str, url: str, user_id: UUID):
        return await create_user_social_media(client, uid=user_id, name=name, url=url)

    return _factory


@pytest.fixture(scope="session")
async def allowed_social_media_site(client):
    return await create_allowed_social_media(
        client, name="Bluebird Braindead App", domain="twitter.com"
    )
