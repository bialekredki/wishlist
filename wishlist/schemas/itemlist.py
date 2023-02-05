from pydantic import Field, validator

from wishlist.schemas.item import Item
from wishlist.schemas.mixins import (
    AuditableMixin,
    DescriptionMixin,
    EditableMixin,
    SlugifyMixin,
    ThumbnailMixin,
    UUIDMixin,
)


class ItemListBase(DescriptionMixin, ThumbnailMixin):
    name: str = Field(..., max_length=64, description="Name of the list.")


class ItemList(ItemListBase, EditableMixin, AuditableMixin, SlugifyMixin, UUIDMixin):
    items: list[Item] = Field(
        default_factory=lambda: [], description="List of items in the wishlist."
    )
    active_list_slug: str | None = Field(default=None)
