from fastapi import FastAPI

from wishlist.config import settings
from wishlist.endpoints import router


def initialize_application():
    app = FastAPI(debug=settings.debug)
    app.include_router(router)
    return app
