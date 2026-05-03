from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ExportFormat = Literal["markdown", "pdf", "word"]


class ExportCreate(BaseModel):
    format: ExportFormat = "markdown"


class ExportResponse(BaseModel):
    id: str
    meeting_id: str = Field(serialization_alias="meetingId")
    format: str
    file_name: str = Field(serialization_alias="fileName")
    file_path: str = Field(serialization_alias="filePath")
    folder_path: str = Field(serialization_alias="folderPath")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = {"from_attributes": True}
