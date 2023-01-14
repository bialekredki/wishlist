from asyncio import gather

from fastapi import status
from httpx import AsyncClient, Response

from tests.utils import assert_http_exception
from wishlist import exceptions

STRONG_PASSWORD = "123StrongPassword!@#"


async def test_user_creation__success(test_client: AsyncClient):
    response = await test_client.post(
        "/user",
        json={"name": "test", "email": "test@test.com", "password": STRONG_PASSWORD},
    )
    assert response.status_code == status.HTTP_200_OK


async def test_user_creation__already_exists(test_client: AsyncClient, user_factory):
    user = await user_factory()
    print(user.email)
    response = await test_client.post(
        "/user",
        json={"name": "test", "email": user.email, "password": STRONG_PASSWORD},
    )
    assert_http_exception(exceptions.already_exists_factory, response)


async def test_user_creation__slug_generation(test_client: AsyncClient):
    responses: list[Response] = await gather(
        *[
            test_client.post(
                "/user",
                json={
                    "name": "test",
                    "email": f"test-b{_}@test.com",
                    "password": STRONG_PASSWORD,
                },
            )
            for _ in range(2**4)
        ]
    )
    assert all(response.status_code == status.HTTP_200_OK for response in responses)
