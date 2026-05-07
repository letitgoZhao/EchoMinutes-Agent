from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.models.note import NoteRecord
from app.prompts.meeting_note import build_meeting_note_prompt
from app.schemas.note import NoteUpdate
from app.services.providers.errors import ProviderRequestError
from app.services.providers.llm.factory import get_llm_provider
from app.services.workflow.transcription_service import get_transcript_segments
from app.utils.logging import get_app_logger

logger = get_app_logger("note")


class NoteWorkflowError(ValueError):
    pass


def get_note(db: Session, meeting_id: str) -> NoteRecord | None:
    statement = select(NoteRecord).where(NoteRecord.meeting_id == meeting_id)
    return db.scalars(statement).first()


def generate_meeting_note(db: Session, meeting_id: str) -> NoteRecord:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise NoteWorkflowError("Meeting not found.")

    segments = get_transcript_segments(db, meeting_id)
    if not segments:
        raise NoteWorkflowError("Transcript is required before generating a note.")

    prompt = build_meeting_note_prompt(segments)
    try:
        provider = get_llm_provider()
        markdown = provider.generate_meeting_note(prompt=prompt, segments=segments)
    except ProviderRequestError as error:
        message = f"DashScope note generation failed: {error.code} - {error.message}"
        logger.error("Meeting note generation failed meeting_id=%s error=%s", meeting_id, error)
        raise NoteWorkflowError(message) from error
    except Exception as error:
        message = "DashScope note generation failed. Check your LLM settings and retry."
        logger.exception("Meeting note generation failed meeting_id=%s", meeting_id)
        raise NoteWorkflowError(message) from error

    note = get_note(db, meeting_id)
    if note is None:
        note = NoteRecord(id=str(uuid4()), meeting_id=meeting_id, markdown=markdown)
        db.add(note)
    else:
        note.markdown = markdown

    db.commit()
    db.refresh(note)
    logger.info(
        "Generated meeting note meeting_id=%s segment_count=%s",
        meeting_id,
        len(segments),
    )
    return note


def save_note(db: Session, meeting_id: str, payload: NoteUpdate) -> NoteRecord:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise NoteWorkflowError("Meeting not found.")

    note = get_note(db, meeting_id)
    if note is None:
        note = NoteRecord(id=str(uuid4()), meeting_id=meeting_id, markdown=payload.markdown)
        db.add(note)
    else:
        note.markdown = payload.markdown

    db.commit()
    db.refresh(note)
    logger.info("Saved meeting note meeting_id=%s", meeting_id)
    return note
