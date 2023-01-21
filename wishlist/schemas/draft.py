import json
from uuid import UUID

from pydantic import BaseModel, Field, validator

from wishlist.schemas.mixins import AuditableMixin, EditableMixin, UUIDMixin


class DraftElementInput(BaseModel):
    name: str = Field(..., max_length=64, description="Name of the draft.")
    draft: dict = Field(default_factory=lambda: {}, description="Draft in JSON format.")

    @validator("draft", pre=True)
    @classmethod
    def __validate_draft(cls, value: dict | str):
        if isinstance(value, dict):
            return value
        return json.loads(value)


class DraftElementOutput(DraftElementInput, AuditableMixin, EditableMixin, UUIDMixin):
    pass


class ListDraft(DraftElementOutput):
    draft_items: list[DraftElementOutput] = Field(
        default_factory=lambda: [], description="List of draft items."
    )


class DraftItemInput(DraftElementInput):
    list_id: UUID = Field(
        ..., description="ID of the list that element will be associated with."
    )
