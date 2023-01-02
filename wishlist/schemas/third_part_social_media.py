from pydantic import BaseModel, Field

from wishlist.schemas.mixins import UUIDMixin


class ThirdPartySocialMediaBase(BaseModel):
    url: str = Field(..., description="Social Media's profile URL.")


class ThirdPartySocialMediaOutput(ThirdPartySocialMediaBase, UUIDMixin):
    name: str = Field(..., description="Social Media's name.")
