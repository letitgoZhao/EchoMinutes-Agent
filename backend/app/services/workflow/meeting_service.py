from pathlib import Path
from shutil import copy2
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate


class MeetingImportError(ValueError):
    pass


def list_meetings(db: Session) -> list[Meeting]:
    statement = select(Meeting).order_by(Meeting.created_at.desc())
    return list(db.scalars(statement).all())


def get_meeting(db: Session, meeting_id: str) -> Meeting | None:
    return db.get(Meeting, meeting_id)


def create_meeting_from_source(db: Session, payload: MeetingCreate) -> Meeting:
    source_path = Path(payload.source_file_path).expanduser().resolve()
    if not source_path.exists() or not source_path.is_file():
        raise MeetingImportError("Selected media file does not exist.")

    meeting_id = str(uuid4())
    media_dir = settings.workspace_dir / "media" / meeting_id
    media_dir.mkdir(parents=True, exist_ok=True)

    target_path = media_dir / source_path.name
    copy2(source_path, target_path)

    meeting = Meeting(
        id=meeting_id,
        title=(payload.title or source_path.stem).strip() or source_path.name,
        source_file_name=source_path.name,
        source_file_path=str(source_path),
        workspace_media_path=str(target_path),
        language=payload.language,
        accent_hint=payload.accent_hint,
        status="imported",
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting
