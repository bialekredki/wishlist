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
    await client.query("SELECT 1;")
    logger.info("Successfully connected to the database.")
