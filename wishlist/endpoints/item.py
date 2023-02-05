import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Security

from wishlist import exceptions, query
from wishlist.database import get_client
from wishlist.endpoints.auth import get_current_user
from wishlist.schemas.draft import (
    DraftElementInputOptionalName,
    DraftElementOutput,
    DraftItemInput,
)
from wishlist.schemas.mixins import UUIDMixin
from wishlist.view import endpoint, view

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
    EXCEPTIONS = {
        "__all__": (
            exceptions.not_found_exception_factory,
            exceptions.FORBIDDEN_EXCEPTION,
            exceptions.AUTHORIZATION_EXCEPTION,
        ),
    }

    RESPONSE_MODEL = {
        "get": DraftElementOutput,
        "post": DraftElementOutput,
        "delete": DraftElementOutput,
        "patch": DraftElementOutput,
    }

    async def get(
        self,
        _id: UUID = Query(..., alias="id"),
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        result = await query.get_draft_item(client, id=_id)
        if result is None:
            raise exceptions.not_found_exception_factory(_id)
        if result.list_draft.owner.id != current_user.id:
            raise exceptions.FORBIDDEN_EXCEPTION
        return result

    async def post(
        self,
        request: DraftItemInput,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        if not (
            await query.get_draft_owned_by_user(
                client, uid=current_user.id, id=request.list_id
            )
        ):
            return exceptions.not_found_exception_factory(request.list_id)

        draft = json.dumps(
            {
                key: value
                for key, value in request.draft.items()
                if not (isinstance(value, list) or isinstance(value, dict))
                and key in ALLOWED_ITEM_DRAFT_FIELDS
            }
        )
        return await query.create_list_item_draft(
            client, name=request.name, draft=draft, list_id=request.list_id
        )

    async def delete(
        self,
        request: UUIDMixin,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        draft_item = await query.get_draft_item(client, id=request.id)
        if not draft_item:
            raise exceptions.not_found_exception_factory(request.id)
        if draft_item.list_draft.owner.id != current_user.id:
            raise exceptions.FORBIDDEN_EXCEPTION
        await query.delete_draft_item(client, id=draft_item.id, uid=current_user.id)
        return draft_item

    @endpoint(("PATCH",), path="/{item_id}")
    async def patch(
        self,
        item_id: UUID,
        request: DraftElementInputOptionalName,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        """Update draft item."""
        draft_item = await query.get_draft_item(client, id=item_id)
        if draft_item is None:
            raise exceptions.not_found_exception_factory(item_id)
        if draft_item.list_draft.owner.id != current_user.id:
            raise exceptions.FORBIDDEN_EXCEPTION
        draft = {
            key: value
            for key, value in request.draft.items()
            if not (isinstance(value, list) or isinstance(value, dict))
            and key in ALLOWED_ITEM_DRAFT_FIELDS
        }
        if draft:
            draft = json.dumps(draft)
        else:
            draft = None
        return await query.update_item_draft(
            client,
            id=item_id,
            name=request.name or draft_item.name,
            draft=draft or draft_item.draft,
        )
