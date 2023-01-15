import pytest
from nanoid import generate

from tests.utils import ALPHANUMERIC_ALPHABET
from wishlist.query import create_user


@pytest.fixture(scope="function")
def user_factory(client, transaction, faker):
    async def _factory(
        *,
        name: str | None = None,
        email: str | None = None,
        password_hash: str = "test",
        slug: str | None = None,
    ):
        base = ""
        if not name or not email or not slug:
            base = generate(size=8, alphabet=ALPHANUMERIC_ALPHABET)
        name = name or f"{faker.name()}{base}"
        email = email or f"{faker.name().replace(' ', '')}{base}@example.test.com"
        slug = slug or base
        user = await create_user(
            client,
            name=name,
            email=email,
            password_hash=password_hash,
            slug=slug,
        )
        return type(
            "UserFactoryWrapperObject",
            (object,),
            {"name": name, "email": email, "slug": slug, "id": user.id},
        )

    yield _factory
