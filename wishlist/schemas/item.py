from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Field,
    FilePath,
    NonNegativeFloat,
    NonNegativeInt,
    root_validator,
)

from wishlist.schemas.mixins import (
    AuditableMixin,
    DescriptionMixin,
    EditableMixin,
    ThumbnailMixin,
    UUIDMixin,
)


class ItemBase(ThumbnailMixin, DescriptionMixin):
    name: str = Field(..., max_length=64, description="Name of the item.")
    price: NonNegativeFloat | None = Field(
        None, description="Estimated price of an item."
    )
    max_price: NonNegativeFloat | None = Field(None, description="Maximal price.")
    min_price: NonNegativeFloat | None = Field(None, description="Minimal price.")
    count: NonNegativeInt | None = Field(
        None, description="Count of items on the wishlist."
    )
    url: AnyHttpUrl | None = Field(
        None, exclusiveMaxiumum=4096, description="URL to the store with the item."
    )

    @root_validator
    @classmethod
    def __root_validator(cls, values):
        if (
            "max_price" in values
            and "min_price" in values
            and values["max_price"]
            and values["min_price"]
            and values["max_price"] < values["min_price"]
        ):
            raise ValueError("Maximal price can't be lower than the minimal price.")

        return values


class Item(ItemBase, EditableMixin, AuditableMixin, UUIDMixin):
    pass
