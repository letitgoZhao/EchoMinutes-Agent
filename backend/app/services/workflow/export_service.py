import re
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.export import ExportRecord
from app.models.meeting import Meeting
from app.services.export.markdown import write_markdown_export
from app.services.export.pdf import write_pdf_export
from app.services.export.word import write_word_export
from app.services.workflow.note_service import get_note
from app.utils.logging import get_app_logger

logger = get_app_logger("export")

class ExportWorkflowError(ValueError):
    pass


def list_exports(db: Session, meeting_id: str) -> list[ExportRecord]:
    statement = (
        select(ExportRecord)
        .where(ExportRecord.meeting_id == meeting_id)
        .order_by(ExportRecord.created_at.desc())
    )
    return list(db.scalars(statement).all())


def create_export(db: Session, meeting_id: str, export_format: str) -> ExportRecord:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise ExportWorkflowError("Meeting not found.")

    note = get_note(db, meeting_id)
    if note is None or not note.markdown.strip():
        raise ExportWorkflowError("A saved note is required before export.")

    if export_format not in {"markdown", "pdf", "word"}:
        raise ExportWorkflowError("Unsupported export format.")

    export_id = str(uuid4())
    export_folder = settings.workspace_dir / "exports" / meeting_id
    extension = _extension_for_format(export_format)
    file_name = f"{_slugify(meeting.title)}-{export_id[:8]}.{extension}"
    target_path = export_folder / file_name
    if export_format == "markdown":
        write_markdown_export(note.markdown, target_path)
    elif export_format == "pdf":
        write_pdf_export(meeting.title, note.markdown, target_path)
    else:
        write_word_export(meeting.title, note.markdown, target_path)

    export = ExportRecord(
        id=export_id,
        meeting_id=meeting_id,
        format=export_format,
        file_name=file_name,
        file_path=str(target_path),
        folder_path=str(export_folder),
    )
    db.add(export)
    db.commit()
    db.refresh(export)
    logger.info(
        "Created export meeting_id=%s export_id=%s format=%s",
        meeting_id,
        export.id,
        export_format,
    )
    return export


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return slug.lower() or "meeting-note"


def _extension_for_format(export_format: str) -> str:
    if export_format == "markdown":
        return "md"
    if export_format == "pdf":
        return "pdf"
    return "docx"
