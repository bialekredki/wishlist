from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, FilePath, validator


class UUIDMixin(BaseModel):
    id: UUID = Field(..., description="Model's ID.")


class SlugifyMixin(BaseModel):
    slug: str = Field(..., description="Model's slug.")


class AuditableMixin(BaseModel):
    created_at: datetime = Field(..., description="Creation datetime.")


class EditableMixin(BaseModel):
    last_edit_at: datetime = Field(..., description="Timestamp of the last edit.")


class ThumbnailMixin(BaseModel):
    thumbnail: AnyHttpUrl | None = Field(
        None, exclusiveMaximum=4096, description="Location of the thumbnail."
    )


class DescriptionMixin(BaseModel):
    description: str | None = Field(
        None, exclusiveMaximum=256, description="Description."
    )
