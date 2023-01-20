import asyncio
import json
import logging

from fastapi import APIRouter, Depends, Query, Security

from wishlist import exceptions, query
from wishlist.database import get_client
from wishlist.endpoints.auth import get_current_user
from wishlist.endpoints.item import ALLOWED_ITEM_DRAFT_FIELDS
from wishlist.schemas.item import DraftElementInput, DraftElementOutput, ListDraft
from wishlist.schemas.mixins import UUID, UUIDMixin
from wishlist.view import view

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
        "get": (
            exceptions.not_found_exception_factory,
            exceptions.AUTHORIZATION_EXCEPTION,
            exceptions.FORBIDDEN_EXCEPTION,
        ),
        "post": (exceptions.AUTHORIZATION_EXCEPTION,),
        "delete": (
            exceptions.AUTHORIZATION_EXCEPTION,
            exceptions.not_found_exception_factory,
            exceptions.FORBIDDEN_EXCEPTION,
        ),
    }

    RESPONSE_MODEL = {"get": ListDraft, "post": ListDraft, "delete": UUIDMixin}

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
        if (await query.get_user_draft_count(client, uid=current_user.id)) > 10:
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
