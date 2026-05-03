from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.models.task import ProcessingTask
from app.models.transcript_segment import TranscriptSegmentRecord
from app.schemas.transcript import TranscriptSegment
from app.services.providers.asr.mock import MockASRProvider
from app.utils.logging import get_app_logger

logger = get_app_logger("transcription")

class TranscriptionError(ValueError):
    pass


class TaskRetryError(ValueError):
    pass


def get_transcript_segments(db: Session, meeting_id: str) -> list[TranscriptSegment]:
    statement = (
        select(TranscriptSegmentRecord)
        .where(TranscriptSegmentRecord.meeting_id == meeting_id)
        .order_by(TranscriptSegmentRecord.start_ms.asc())
    )
    records = list(db.scalars(statement).all())
    return [
        TranscriptSegment(
            id=record.id,
            speaker=record.speaker,
            start_ms=record.start_ms,
            end_ms=record.end_ms,
            text=record.text,
            confidence=record.confidence,
        )
        for record in records
    ]


def transcribe_meeting_with_mock(db: Session, meeting_id: str) -> Meeting:
    task = create_transcription_task(db, meeting_id)
    meeting = _run_mock_transcription_for_task(db, task)
    return meeting


def list_transcription_tasks(db: Session, meeting_id: str) -> list[ProcessingTask]:
    statement = (
        select(ProcessingTask)
        .where(
            ProcessingTask.meeting_id == meeting_id,
            ProcessingTask.kind == "transcription",
        )
        .order_by(ProcessingTask.created_at.desc())
    )
    return list(db.scalars(statement).all())


def create_transcription_task(db: Session, meeting_id: str) -> ProcessingTask:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise TranscriptionError("Meeting not found.")

    task = ProcessingTask(
        id=str(uuid4()),
        meeting_id=meeting_id,
        kind="transcription",
        status="queued",
        attempt_count=1,
        retryable=False,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(
        "Queued transcription task meeting_id=%s task_id=%s attempt=%s",
        meeting_id,
        task.id,
        task.attempt_count,
    )
    return task


def retry_transcription_task(db: Session, meeting_id: str, task_id: str) -> ProcessingTask:
    task = db.get(ProcessingTask, task_id)
    if task is None or task.meeting_id != meeting_id or task.kind != "transcription":
        raise TaskRetryError("Transcription task not found.")

    if not task.retryable and task.status != "failed":
        raise TaskRetryError("Transcription task is not retryable.")

    task.status = "queued"
    task.retryable = False
    task.error_message = None
    task.attempt_count += 1
    db.commit()
    db.refresh(task)
    return task


def run_transcription_task_with_mock(db: Session, task: ProcessingTask) -> Meeting:
    return _run_mock_transcription_for_task(db, task)


def _run_mock_transcription_for_task(db: Session, task: ProcessingTask) -> Meeting:
    meeting = db.get(Meeting, task.meeting_id)
    if meeting is None:
        _fail_task(db, task, "Meeting not found.", retryable=False)
        raise TranscriptionError("Meeting not found.")

    meeting.status = "transcribing"
    meeting.error_message = None
    task.status = "running"
    task.retryable = False
    task.error_message = None
    db.commit()

    try:
        if not meeting.workspace_media_path:
            raise TranscriptionError("Meeting media is not available for transcription.")

        provider = MockASRProvider()
        segments = provider.transcribe(meeting.workspace_media_path)

        db.execute(
            delete(TranscriptSegmentRecord).where(
                TranscriptSegmentRecord.meeting_id == task.meeting_id
            )
        )
        db.add_all(
            [
                TranscriptSegmentRecord(
                    id=f"{task.meeting_id}:{segment.id}",
                    meeting_id=task.meeting_id,
                    speaker=segment.speaker,
                    start_ms=segment.start_ms,
                    end_ms=segment.end_ms,
                    text=segment.text,
                    confidence=segment.confidence,
                )
                for segment in segments
            ]
        )
        meeting.status = "transcribed"
        task.status = "succeeded"
        task.retryable = False
        task.error_message = None
        db.commit()
        db.refresh(meeting)
        db.refresh(task)
        logger.info(
            "Completed transcription meeting_id=%s task_id=%s segments=%s",
            meeting.id,
            task.id,
            len(segments),
        )
        return meeting
    except TranscriptionError as error:
        meeting.status = "failed"
        meeting.error_message = str(error)
        _fail_task(db, task, str(error), retryable=True)
        db.refresh(meeting)
        logger.error(
            "Transcription failed meeting_id=%s task_id=%s error=%s",
            task.meeting_id,
            task.id,
            error,
        )
        raise


def rename_speaker(
    db: Session,
    meeting_id: str,
    current_speaker: str,
    new_speaker: str,
) -> list[TranscriptSegment]:
    cleaned_name = new_speaker.strip()
    if not cleaned_name:
        raise TranscriptionError("Speaker name cannot be empty.")

    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise TranscriptionError("Meeting not found.")

    statement = select(TranscriptSegmentRecord).where(
        TranscriptSegmentRecord.meeting_id == meeting_id,
        TranscriptSegmentRecord.speaker == current_speaker,
    )
    records = list(db.scalars(statement).all())
    if not records:
        raise TranscriptionError("Speaker not found in transcript.")

    for record in records:
        record.speaker = cleaned_name

    db.commit()
    logger.info(
        "Renamed speaker meeting_id=%s from=%s to=%s",
        meeting_id,
        current_speaker,
        cleaned_name,
    )
    return get_transcript_segments(db, meeting_id)


def update_transcript_segment(
    db: Session,
    meeting_id: str,
    segment_id: str,
    text: str,
) -> TranscriptSegment:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise TranscriptionError("Transcript text cannot be empty.")

    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise TranscriptionError("Meeting not found.")

    segment = db.get(TranscriptSegmentRecord, segment_id)
    if segment is None or segment.meeting_id != meeting_id:
        raise TranscriptionError("Transcript segment not found.")

    segment.text = cleaned_text
    db.commit()
    logger.info(
        "Updated transcript segment meeting_id=%s segment_id=%s",
        meeting_id,
        segment_id,
    )

    return TranscriptSegment(
        id=segment.id,
        speaker=segment.speaker,
        start_ms=segment.start_ms,
        end_ms=segment.end_ms,
        text=segment.text,
        confidence=segment.confidence,
    )


def _fail_task(
    db: Session,
    task: ProcessingTask,
    error_message: str,
    retryable: bool,
) -> None:
    task.status = "failed"
    task.retryable = retryable
    task.error_message = error_message
    db.commit()
