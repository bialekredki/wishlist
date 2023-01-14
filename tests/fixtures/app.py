import os
from asyncio import wait_for
from unittest import mock

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient

from wishlist import initialize_application


@pytest.fixture(scope="session")
def app(database_name):
    with mock.patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
        app = initialize_application()
        yield app


@pytest.fixture(scope="session")
async def test_client(app: FastAPI, database_name):
    async with AsyncClient(
        app=app, base_url="http://base_test"
    ) as client, LifespanManager(app):
        yield client
        await wait_for(client.aclose(), 10)
