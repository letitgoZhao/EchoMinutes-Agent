from datetime import datetime

from pydantic import BaseModel, Field


class NoteResponse(BaseModel):
    id: str | None = None
    meeting_id: str | None = Field(default=None, serialization_alias="meetingId")
    markdown: str
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
    updated_at: datetime | None = Field(default=None, serialization_alias="updatedAt")

    model_config = {"from_attributes": True}


class NoteUpdate(BaseModel):
    markdown: str
