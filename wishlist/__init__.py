import logging

from fastapi import FastAPI

from wishlist.config import settings
from wishlist.database import connect_to_the_database
from wishlist.endpoints import router


def initialize_application():
    app = FastAPI(debug=settings.debug)

    logging.basicConfig(level=settings.log_level)

    app.include_router(router)

    @app.on_event("startup")
    async def app_startup_routine():
        await connect_to_the_database()

    return app
