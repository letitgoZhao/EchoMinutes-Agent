from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    id: str
    speaker: str
    start_ms: int = Field(serialization_alias="startMs")
    end_ms: int = Field(serialization_alias="endMs")
    text: str
    confidence: float
