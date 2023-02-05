import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from wishlist.config import settings
from wishlist.database import connect_to_the_database, disconnect_from_the_database
from wishlist.endpoints import router


def initialize_application():
    app = FastAPI(debug=settings.debug)

    logging.basicConfig(level=settings.log_level)

    app.include_router(router)

    if settings.ALLOW_CORS:
        logging.info(f"Allowing CORS from {' '.join(settings.ALLOW_CORS)}")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOW_CORS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.on_event("startup")
    async def app_startup_routine():
        await connect_to_the_database()

    @app.on_event("shutdown")
    async def app_shutdown_routine():
        await disconnect_from_the_database()

    return app
