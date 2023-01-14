import asyncio
import logging
from functools import cache

import edgedb

logger = logging.getLogger("wishlist-database")


@cache
def get_client():
    return edgedb.create_async_client()


async def connect_to_the_database():
    logger.info("Trying to connect to the database.")
    client = get_client()
    await client.ensure_connected()
    logger.info("Successfully connected to the database.")


async def disconnect_from_the_database():
    client = get_client()
    logger.info("Trying to disconnect from the database.")
    await asyncio.wait_for(client.aclose(), 10)
    logger.info("Successfully disconnected from the database.")
