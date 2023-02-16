import asyncio
import os
import subprocess
import time
from datetime import datetime, timedelta
from unittest import mock

import pytest
import pytest_asyncio
from edgedb import AsyncIOClient, create_async_client
from nanoid import generate

from tests.utils import ALPHANUMERIC_ALPHABET, Rollback
from tests.edgedb_cli import retryable_command


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database_name():
    name = generate(
        size=10,
        alphabet=ALPHANUMERIC_ALPHABET,
    )
    retryable_command(["edgedb", "query", f"create database {name}"], b"OK")
    with mock.patch.dict(os.environ, {"EDGEDB_DATABASE": name}):
        proc = subprocess.Popen(
            ["edgedb", "migration", "apply"], stderr=subprocess.PIPE
        )
        proc.communicate()
        yield name
    retryable_command(["edgedb", "query", f"drop database {name}"], b"OK")


@pytest_asyncio.fixture(scope="session")
async def client(database_name):
    client = create_async_client()
    await client.ensure_connected()
    yield client
    await asyncio.wait_for(client.aclose(), 30)


@pytest_asyncio.fixture(scope="session")
async def transaction(client: AsyncIOClient):
    try:
        async for tx in client.transaction():
            async with tx:
                yield tx
                raise Rollback()
    except Rollback:
        pass
