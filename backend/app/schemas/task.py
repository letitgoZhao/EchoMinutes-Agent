from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.meeting import MeetingResponse


class ProcessingTaskResponse(BaseModel):
    id: str
    meeting_id: str = Field(serialization_alias="meetingId")
    kind: str
    status: str
    attempt_count: int = Field(serialization_alias="attemptCount")
    retryable: bool
    error_message: str | None = Field(serialization_alias="errorMessage")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    model_config = {"from_attributes": True}


class TranscriptionTaskRunResponse(BaseModel):
    task: ProcessingTaskResponse
    meeting: MeetingResponse
