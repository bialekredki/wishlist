from pydantic import BaseModel, Field, HttpUrl, validator

from wishlist.schemas.mixins import UUIDMixin


class ThirdPartySocialMediaBase(BaseModel):
    url: HttpUrl = Field(..., description="Social Media's profile URL.")

    @validator("url")
    @classmethod
    def __validate_url(cls, value: HttpUrl):
        if value.scheme == "http":
            raise ValueError("URL needs to have HTTPS schema.")
        return value


class ThirdPartySocialMediaOutput(ThirdPartySocialMediaBase, UUIDMixin):
    name: str = Field(..., description="Social Media's name.")


class AllowedThirdPartySocialMedia(UUIDMixin):
    name: str = Field(..., description="Name of the allowed social media site.")
    domain: str = Field(..., description="Domain for the social media site.")
