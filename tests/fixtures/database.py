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


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def database_drop_timeout_ms():
    return os.environ.get("PYTEST_EDGDE_DROP_TIMEOUT_MS", 12_000)


@pytest.fixture(scope="session")
def database_drop_retries_limit():
    return os.environ.get("PYTEST_EDGDE_DROP_RETRY_LIMIT", 256)


@pytest.fixture(scope="session")
def database_name(database_drop_timeout_ms, database_drop_retries_limit):
    name = generate(
        size=10,
        alphabet=ALPHANUMERIC_ALPHABET,
    )
    proc = subprocess.Popen(
        ["edgedb", "query", f"create database {name}"], stderr=subprocess.PIPE
    )
    assert (
        b"OK" in proc.communicate()[1]
    ), f"Database creation({name}) command didn't return OK status."
    with mock.patch.dict(os.environ, {"EDGEDB_DATABASE": name}):
        proc = subprocess.Popen(
            ["edgedb", "migration", "apply"], stderr=subprocess.PIPE
        )
        proc.communicate()
        yield name

    start = datetime.now()
    is_ok = False
    stderr = None
    attempts = 0
    while (
        timedelta(milliseconds=database_drop_timeout_ms) >= datetime.now() - start
        and database_drop_retries_limit > attempts
    ):
        attempts += 1
        proc = subprocess.Popen(
            ["edgedb", "query", f"drop database {name}"], stderr=subprocess.PIPE
        )
        stderr = proc.communicate()[1]
        is_ok = b"OK" in stderr
        if is_ok:
            break
        time.sleep(0.1)
    assert is_ok, f"Dropping database {name} timed out. Last fail was {stderr}."


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
