from uuid import UUID

from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    id: UUID = Field(..., description="Model's ID.")


class SlugifyMixin(BaseModel):
    slug: str = Field(..., description="Model's slug.")
