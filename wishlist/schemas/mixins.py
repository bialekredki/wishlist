from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    id: UUID = Field(..., description="Model's ID.")


class SlugifyMixin(BaseModel):
    slug: str = Field(..., description="Model's slug.")


class AuditableMixin(BaseModel):
    created_at: datetime = Field(..., description="Creation datetime.")


class EditableMixin(BaseModel):
    last_edit_at: datetime = Field(..., description="Timestamp of the last edit.")
