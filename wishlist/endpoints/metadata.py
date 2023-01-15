import logging

from fastapi import APIRouter, Depends

from wishlist.query import get_allowed_social_media
from wishlist.schemas.third_part_social_media import AllowedThirdPartySocialMedia
from wishlist.database import get_client

logger = logging.getLogger("metadata-endpoints")
router = APIRouter()


@router.get(
    "/allowed_social_media_sites", response_model=list[AllowedThirdPartySocialMedia]
)
async def allowed_social_media_sites(client=Depends(get_client)):
    return await get_allowed_social_media(client)
