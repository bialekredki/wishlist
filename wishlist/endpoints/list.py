import asyncio
import json
import logging

import orjson
from edgedb.errors import ConstraintViolationError
from fastapi import APIRouter, Depends, Query, Security
from nanoid import generate
from pydantic import ValidationError

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
from wishlist.schemas.item import Item
from wishlist.schemas.itemlist import ItemList
from wishlist.schemas.mixins import UUID, UUIDMixin
from wishlist.view import endpoint, view

logger = logging.getLogger("list-endpoints")
router = APIRouter()
ALLOWED_LIST_DRAFT_FIELDS = ("thumbnail", "description")


async def create_draft_list(
    input: DraftElementInput, client, current_user, active_version_slug=None
):
    if (
        await query.get_user_draft_count(client, uid=current_user.id)
    ) >= settings.drafts_max_ammount:
        raise exceptions.TOO_MANY_DRAFTS
    draft = {
        key: value
        for key, value in input.draft.items()
        if key in ALLOWED_LIST_DRAFT_FIELDS
    }
    draft_items = (
        {
            key: value
            for key, value in draft_item.items()
            if key in ALLOWED_ITEM_DRAFT_FIELDS
        }
        for draft_item in input.draft.get("draft_items", [])
        if isinstance(draft_item, dict)
    )
    try:
        result = await query.create_list_draft(
            client,
            name=input.name,
            draft=json.dumps(draft),
            uid=current_user.id,
            list_slug=active_version_slug,
        )
    except ConstraintViolationError as exc:
        raise exceptions.already_exists_factory(
            f"from {active_version_slug}", "ListDraft"
        ) from exc
    draft_items = await asyncio.gather(
        *(
            query.create_list_item_draft(
                client,
                name=draft_item.get("name") or "item",
                draft=json.dumps(draft_item),
                list_id=result.id,
            )
            for draft_item in draft_items
        )
    )
    return await query.get_draft_owned_by_user(
        client, uid=current_user.id, id=result.id
    )


@view(router, path="/list")
class ListView:

    RESPONSE_MODEL = {"get": ItemList}

    EXCEPTIONS = {"get": (exceptions.not_found_exception_factory,)}

    @endpoint(path="/{slug}")
    async def get(self, slug: str, client=Depends(get_client)):
        _list = await query.get_list_by_slug(client, slug=slug)
        if _list is None:
            raise exceptions.not_found_exception_factory(slug)
        return _list

    @endpoint(methods=("post",), path="/{slug}")
    async def edit(
        self,
        slug: str,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        _list = await query.get_list_by_slug(client, slug=slug)
        if _list is None:
            raise exceptions.not_found_exception_factory(slug)
        if current_user.id != _list.owner.id:
            raise exceptions.FORBIDDEN_EXCEPTION
        draf_items = [
            dict(
                thumbnail=item.thumbnail,
                name=item.name,
                description=item.description,
                price=item.price,
                max_price=item.max_price,
                min_price=item.min_price,
                count=item.count,
                url=item.url,
            )
            for item in _list.items
        ]
        draft = DraftElementInput(
            draft=dict(
                thumbnail=_list.thumbnail,
                description=_list.description,
                draft_items=draf_items,
            ),
            name=_list.name,
        )
        return await create_draft_list(
            draft, client, current_user, active_version_slug=_list.slug
        )


@view(router, path="/draft/list")
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
        "validate": (
            exceptions.not_found_exception_factory,
            exceptions.FORBIDDEN_EXCEPTION,
        ),
    }

    RESPONSE_MODEL = {
        "get": ListDraft,
        "post": ListDraft,
        "delete": UUIDMixin,
        "patch": DraftElementOutput,
    }

    @endpoint(path="/{list_id}")
    async def get(
        self,
        list_id: UUID,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):

        result = await query.get_draft_owned_by_user(
            client, uid=current_user.id, id=list_id
        )
        if result:
            return result
        raise exceptions.not_found_exception_factory(list_id)

    async def post(
        self,
        request: DraftElementInput,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        return await create_draft_list(request, client, current_user)

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

    @endpoint(methods={"get"}, path="/{list_id}/validate")
    async def validate(
        self,
        list_id: UUID,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        list_draft = await query.get_draft_owned_by_user(
            client, uid=current_user.id, id=list_id
        )
        if list_draft is None:
            raise exceptions.not_found_exception_factory(list_id)
        items = []
        for draft_item in list_draft.draft_items:
            draft = orjson.loads(draft_item.draft)
            draft_object = {
                "name": draft_item.name,
                "id": draft_item.id,
                "created_at": draft_item.created_at,
                "last_edit_at": draft_item.last_edit_at,
                **draft,
            }
            try:
                items.append(Item.validate(draft_object))
            except ValidationError as exc:
                raise exceptions.draft_validation_exception_factory(
                    exc, draft_item.id
                ) from exc
        draft = list_draft.draft
        if draft.endswith('"') or draft.endswith("'"):
            draft = draft[:-1]
        if draft.startswith('"') or draft.startswith("'"):
            draft = draft[1:]
        draft = orjson.loads(draft)
        slug = list_draft.active_list_slug or f"{list_draft.name}__{generate(size=12)}"
        draft_object = {
            "name": list_draft.name,
            "id": list_draft.id,
            "created_at": list_draft.created_at,
            "last_edit_at": list_draft.last_edit_at,
            "slug": slug,
        }
        draft_object.update(draft)
        try:
            item_list = ItemList.validate(draft_object)
        except ValidationError as exc:
            raise exceptions.draft_validation_exception_factory(
                exc, list_draft.id
            ) from exc
        item_list.items = items
        return item_list

    @endpoint(methods=("PUT",), path="/{list_id}/save")
    async def save(
        self,
        list_id: UUID,
        client=Depends(get_client),
        current_user=Security(get_current_user),
    ):
        """Saves draft as a Wishlist."""
        validated_model = await self.validate(list_id, client, current_user)

        try:
            _list = await query.create_list(
                client,
                name=validated_model.name,
                thumbnail=str(validated_model.thumbnail),
                description=validated_model.description,
                slug=validated_model.slug,
                uid=current_user.id,
            )
        except ConstraintViolationError:
            _list = await query.update_list(
                client,
                slug=validated_model.slug,
                name=validated_model.name,
                thumbnail=str(validated_model.thumbnail),
                description=validated_model.description,
            )
            if _list is None:
                raise ValueError(
                    f"Updating list of slug {validated_model.slug} failed."
                )
            await query.clear_items_in_list(client, list_id=_list.id)
        items = await asyncio.gather(
            *(
                query.create_list_item(
                    client,
                    list_id=_list.id,
                    **{
                        key: value
                        for key, value in item.dict().items()
                        if key not in ("id", "created_at", "last_edit_at")
                    },
                )
                for item in validated_model.items
            )
        )
        await query.delete_list_draft(
            client, id=validated_model.id, uid=current_user.id
        )
        return ItemList(
            id=_list.id,
            items=[
                Item(
                    id=item.id,
                    created_at=item.created_at,
                    last_edit_at=item.last_edit_at,
                    description=item.description,
                    name=item.name,
                    price=item.price,
                    thumbnail=item.thumbnail,
                    max_price=item.max_price,
                    min_price=item.min_price,
                    count=item.count,
                    url=item.url,
                )
                for item in items
            ],
            name=_list.name,
            slug=_list.slug,
            thumbnail=_list.thumbnail,
            created_at=_list.created_at,
            last_edit_at=_list.last_edit_at,
            description=_list.description,
        )
