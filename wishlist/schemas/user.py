from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from wishlist.schemas.mixins import SlugifyMixin, UUIDMixin
from wishlist.schemas.third_part_social_media import ThirdPartySocialMediaOutput
from wishlist.security import is_password_safe


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
    password: str = Field(
        ..., description="User's password.", max_length=127, min_length=8
    )

    @validator("password")
    @classmethod
    def _validate_password(cls, value: str):
        if is_password_safe(value):
            return value
        raise ValueError("Password is not strong enough.")


class DetailedUser(UsernameMixin, SlugifyMixin, UUIDMixin):
    bio: str = Field(
        default=None, description="User's short description.", max_length=512
    )
    third_party_social_media: list[ThirdPartySocialMediaOutput] = Field(
        default_factory=lambda: None, description="Linked social media to account."
    )
