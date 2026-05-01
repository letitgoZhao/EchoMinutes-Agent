from fastapi import APIRouter

from app.schemas.note import NoteResponse
from app.schemas.transcript import TranscriptSegment
from app.services.providers.asr.mock import MockASRProvider
from app.services.providers.llm.mock import MockLLMProvider

router = APIRouter()


@router.get("/transcript", response_model=list[TranscriptSegment])
async def get_mock_transcript() -> list[TranscriptSegment]:
    provider = MockASRProvider()
    return provider.transcribe_placeholder()


@router.get("/note", response_model=NoteResponse)
async def get_mock_note() -> NoteResponse:
    provider = MockLLMProvider()
    return NoteResponse(markdown=provider.generate_placeholder_note())
