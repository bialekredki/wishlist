import logging
from collections.abc import Iterable

from fastapi import APIRouter, Security
from yarl import URL

import wishlist.exceptions as exceptions
import wishlist.query as dbquery
from wishlist.database import client
from wishlist.endpoints.auth import get_current_user
from wishlist.schemas.mixins import UUIDMixin
from wishlist.schemas.user import UsersSocialMedia
from wishlist.schemas.third_part_social_media import (
    ThirdPartySocialMediaBase,
    ThirdPartySocialMediaOutput,
)
from wishlist.view import view

logger = logging.getLogger("myself-endpoints")
router = APIRouter()


@view(router, path="/social_media")
class MySocialMediaView:

    EXCEPTIONS = {
        "__all__": (exceptions.AUTHORIZATION_EXCEPTION,),
        "post": (
            exceptions.NOT_SUPPORTED_SOCIAL_MEDIA_SITE,
            exceptions.REQUIRE_HTTPS_EXCEPTION,
        ),
    }

    RESPONSE_MODEL = {"get": UsersSocialMedia}

    async def get(self, current_user=Security(get_current_user)):
        """Get My Linked Social Media Accounts"""
        return await dbquery.get_user_social_media(client, id=current_user.id)

    async def post(
        self,
        request: ThirdPartySocialMediaBase,
        current_user=Security(get_current_user),
    ):
        """Link new social media account to my profile."""
        allowed_social_media = await dbquery.get_allowed_social_media(client)
        url = URL(request.url)
        if url.scheme != "https":
            raise exceptions.REQUIRE_HTTPS_EXCEPTION
        social_media = [sm for sm in allowed_social_media if url.host == sm.domain]
        if len(social_media) == 0:
            raise exceptions.NOT_SUPPORTED_SOCIAL_MEDIA_SITE
        social_media = social_media[0]
        return await dbquery.create_user_social_media(
            client, url=request.url, uid=current_user.id, name=social_media.name
        )

    async def delete(self, request: UUIDMixin, current_user=Security(get_current_user)):
        """Delete linked social media account."""
        return await dbquery.delete_users_social_media(
            client, id=request.id, uid=current_user.id
        )
