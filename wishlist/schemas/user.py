from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from wishlist.schemas.mixins import SlugifyMixin, UUIDMixin
from wishlist.schemas.third_part_social_media import ThirdPartySocialMediaOutput


class UsernameMixin(BaseModel):
    name: str = Field(..., description="Username.")


class PublicUser(UsernameMixin, SlugifyMixin, UUIDMixin):
    country_code: str | None = Field(
        default=None, description="Country code specified by user."
    )


class UsersSocialMedia(UUIDMixin):
    third_party_social_media: list[ThirdPartySocialMediaOutput] = Field(
        default_factory=lambda: [], description="Linked social media account to user."
    )


class CreateUser(UsernameMixin):
    email: EmailStr = Field(..., description="User's email.")
    password: str = Field(..., description="User's password.")


class DetailedUser(UsernameMixin, SlugifyMixin, UUIDMixin):
    bio: str = Field(
        default=None, description="User's short description.", max_length=512
    )
    third_party_social_media: list[ThirdPartySocialMediaOutput] = Field(
        default_factory=lambda: None, description="Linked social media to account."
    )
