import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Query, Security

from wishlist import exceptions, query
from wishlist.config import settings
from wishlist.database import get_client
from wishlist.endpoints.auth import get_current_user
from wishlist.endpoints.item import ALLOWED_ITEM_DRAFT_FIELDS
from wishlist.schemas.draft import (
    DraftElementInput,
    DraftElementInputOptionalName,
    DraftElementOutput,
    ListDraft,
)
from wishlist.schemas.mixins import UUID, UUIDMixin
from wishlist.view import endpoint, view

logger = logging.getLogger("list-endpoints")
router = APIRouter()
ALLOWED_LIST_DRAFT_FIELDS = ("thumbnail", "description")


@view(router, path="/list")
class ListView:
    async def get(self):
        pass


@view(router, path="/list/draft")
class ListDraftView:

    EXCEPTIONS = {
        "__all__": (exceptions.AUTHORIZATION_EXCEPTION,),
        "get": (
            exceptions.not_found_exception_factory,
            exceptions.FORBIDDEN_EXCEPTION,
        ),
        "delete": (
            exceptions.not_found_exception_factory,
            exceptions.FORBIDDEN_EXCEPTION,
        ),
        "patch": (
            exceptions.FORBIDDEN_EXCEPTION,
            exceptions.not_found_exception_factory,
        ),
    }

    RESPONSE_MODEL = {
        "get": ListDraft,
        "post": ListDraft,
        "delete": UUIDMixin,
        "patch": DraftElementOutput,
    }

    async def get(
        self,
        _id: UUID = Query(..., alias="id"),
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):

        result = await query.get_draft_owned_by_user(
            client, uid=current_user.id, id=_id
        )
        if result:
            return result
        raise exceptions.not_found_exception_factory(_id)

    async def post(
        self,
        request: DraftElementInput,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        if (
            await query.get_user_draft_count(client, uid=current_user.id)
        ) >= settings.drafts_max_ammount:
            raise exceptions.TOO_MANY_DRAFTS
        draft = {
            key: value
            for key, value in request.draft.items()
            if key in ALLOWED_LIST_DRAFT_FIELDS
        }
        draft_items = (
            {
                key: value
                for key, value in draft_item.items()
                if key in ALLOWED_ITEM_DRAFT_FIELDS
            }
            for draft_item in request.draft.get("draft_items", [])
            if isinstance(draft_item, dict)
        )
        result = await query.create_list_draft(
            client, name=request.name, draft=json.dumps(draft), uid=current_user.id
        )
        draft_items = await asyncio.gather(
            *(
                query.create_list_item_draft(
                    client, name="test", draft=json.dumps(draft_item), list_id=result.id
                )
                for draft_item in draft_items
            )
        )
        return await query.get_draft_owned_by_user(
            client, uid=current_user.id, id=result.id
        )

    async def delete(
        self,
        request: UUIDMixin,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        result = await query.delete_list_draft(
            client, id=request.id, uid=current_user.id
        )
        if result:
            return result
        raise exceptions.not_found_exception_factory(request.id)

    @endpoint(methods=("patch",), path="/{list_id}")
    async def patch(
        self,
        list_id: UUID,
        request: DraftElementInputOptionalName,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        """Update draft of a list."""
        list_draft = await query.get_draft_owned_by_user(
            client, uid=current_user.id, id=list_id
        )
        if list_draft is None:
            raise exceptions.not_found_exception_factory(list_id)
        draft = json.dumps(
            {
                key: value
                for key, value in request.draft.items()
                if key in ALLOWED_LIST_DRAFT_FIELDS
            }
        )
        return await query.update_list_draft(
            client, id=list_draft.id, name=request.name or list_draft.name, draft=draft
        )
