import logging

from fastapi import APIRouter

from wishlist.view import view

logger = logging.getLogger("item-endpoints")
router = APIRouter()
ALLOWED_ITEM_DRAFT_FIELDS = (
    "thumbnail",
    "description",
    "price",
    "max_price",
    "min_price",
    "count",
    "url",
)


@view(router, path="/item")
class ItemView:
    async def get(self):
        pass


@view(router, path="/item/draft")
class ItemDraftView:
    async def get(self):
        pass
