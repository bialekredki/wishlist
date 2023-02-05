import logging

from fastapi import APIRouter, Depends, Security
from yarl import URL

import wishlist.exceptions as exceptions
import wishlist.query as dbquery
from wishlist.database import get_client
from wishlist.endpoints.auth import get_current_user
from wishlist.schemas.mixins import UUIDMixin
from wishlist.schemas.third_part_social_media import ThirdPartySocialMediaBase
from wishlist.schemas.user import UsersSocialMedia, PublicUser
from wishlist.view import view

logger = logging.getLogger("myself-endpoints")
router = APIRouter()


@router.get("/basic_info", response_model=PublicUser)
async def get_my_basic_information(
    client=Depends(get_client), current_user=Security(get_current_user)
):
    return (await dbquery.get_user_by_slug(client, slug=current_user.slug))[0]


@view(router, path="/social_media")
class MySocialMediaView:

    EXCEPTIONS = {
        "__all__": (exceptions.AUTHORIZATION_EXCEPTION,),
        "post": (exceptions.NOT_SUPPORTED_SOCIAL_MEDIA_SITE,),
    }

    RESPONSE_MODEL = {"get": UsersSocialMedia}

    async def get(
        self, client=Depends(get_client), current_user=Security(get_current_user)
    ):
        """Get My Linked Social Media Accounts"""
        return await dbquery.get_user_social_media(client, id=current_user.id)

    async def post(
        self,
        request: ThirdPartySocialMediaBase,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        """Link new social media account to my profile."""
        allowed_social_media = await dbquery.get_allowed_social_media(client)
        url = URL(request.url)
        social_media = [sm for sm in allowed_social_media if url.host == sm.domain]
        if len(social_media) == 0:
            raise exceptions.NOT_SUPPORTED_SOCIAL_MEDIA_SITE
        social_media = social_media[0]
        return await dbquery.create_user_social_media(
            client, url=request.url, uid=current_user.id, name=social_media.name
        )

    async def delete(
        self,
        request: UUIDMixin,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        """Delete linked social media account."""
        result = await dbquery.delete_users_social_media(
            client, id=request.id, uid=current_user.id
        )
        print(result)
        if result:
            return result
        raise exceptions.not_found_exception_factory(request.id)


@view(router, path="/drafts")
class MyDraftsView:
    EXCEPTIONS = {"get": (exceptions.AUTHORIZATION_EXCEPTION,)}

    async def get(
        self, client=Depends(get_client), current_user=Depends(get_current_user)
    ):
        return await dbquery.get_users_list_drafts(client, uid=current_user.id)


@view(router, path="/lists")
class MyListView:
    EXCEPTIONS = {"get": (exceptions.AUTHORIZATION_EXCEPTION,)}

    async def get(
        self, client=Depends(get_client), current_user=Depends(get_current_user)
    ):
        return await dbquery.get_users_lists(client, uid=current_user.id)
