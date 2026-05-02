from datetime import datetime

from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    source_file_path: str
    title: str | None = None
    language: str = "auto"
    accent_hint: str | None = None


class MeetingResponse(BaseModel):
    id: str
    title: str
    source_file_name: str = Field(serialization_alias="sourceFileName")
    source_file_path: str = Field(serialization_alias="sourceFilePath")
    workspace_media_path: str = Field(serialization_alias="workspaceMediaPath")
    language: str
    accent_hint: str | None = Field(serialization_alias="accentHint")
    status: str
    duration_seconds: int | None = Field(serialization_alias="durationSeconds")
    error_message: str | None = Field(serialization_alias="errorMessage")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = {"from_attributes": True}
