from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.meeting import MeetingResponse
from app.schemas.task import ProcessingTaskResponse, TranscriptionTaskRunResponse
from app.schemas.transcript import SpeakerRename, TranscriptSegment, TranscriptSegmentUpdate
from app.services.workflow.transcription_service import (
    TaskRetryError,
    TranscriptionError,
    create_transcription_task,
    get_transcript_segments,
    list_transcription_tasks,
    rename_speaker,
    retry_transcription_task,
    run_transcription_task,
    transcribe_meeting,
    update_transcript_segment,
)

router = APIRouter(prefix="/meetings/{meeting_id}")
DbSession = Annotated[Session, Depends(get_db)]


def _workflow_error_to_http(
    error: ValueError,
    *,
    not_found_details: set[str] | None = None,
) -> HTTPException:
    detail = str(error)
    status_code = (
        status.HTTP_404_NOT_FOUND
        if detail in (not_found_details or set())
        else status.HTTP_400_BAD_REQUEST
    )
    return HTTPException(status_code=status_code, detail=detail)


@router.post("/transcribe", response_model=MeetingResponse)
async def transcribe_meeting_endpoint(meeting_id: str, db: DbSession) -> MeetingResponse:
    try:
        return transcribe_meeting(db, meeting_id)
    except TranscriptionError as error:
        raise _workflow_error_to_http(
            error,
            not_found_details={"Meeting not found."},
        ) from error


@router.get("/transcription-tasks", response_model=list[ProcessingTaskResponse])
async def read_transcription_tasks(
    meeting_id: str,
    db: DbSession,
) -> list[ProcessingTaskResponse]:
    return list_transcription_tasks(db, meeting_id)


@router.post("/transcription-tasks", response_model=TranscriptionTaskRunResponse)
async def start_transcription_task(
    meeting_id: str,
    db: DbSession,
) -> TranscriptionTaskRunResponse:
    try:
        task = create_transcription_task(db, meeting_id)
        meeting = run_transcription_task(db, task)
        return TranscriptionTaskRunResponse(task=task, meeting=meeting)
    except TranscriptionError as error:
        raise _workflow_error_to_http(
            error,
            not_found_details={"Meeting not found."},
        ) from error


@router.post(
    "/transcription-tasks/{task_id}/retry",
    response_model=TranscriptionTaskRunResponse,
)
async def retry_transcription(
    meeting_id: str,
    task_id: str,
    db: DbSession,
) -> TranscriptionTaskRunResponse:
    try:
        task = retry_transcription_task(db, meeting_id, task_id)
        meeting = run_transcription_task(db, task)
        return TranscriptionTaskRunResponse(task=task, meeting=meeting)
    except TaskRetryError as error:
        raise _workflow_error_to_http(
            error,
            not_found_details={"Transcription task not found."},
        ) from error
    except TranscriptionError as error:
        raise _workflow_error_to_http(error) from error


@router.get("/transcript", response_model=list[TranscriptSegment])
async def read_transcript(meeting_id: str, db: DbSession) -> list[TranscriptSegment]:
    return get_transcript_segments(db, meeting_id)


@router.put("/speakers", response_model=list[TranscriptSegment])
async def update_speaker(
    meeting_id: str,
    payload: SpeakerRename,
    db: DbSession,
) -> list[TranscriptSegment]:
    try:
        return rename_speaker(db, meeting_id, payload.current_speaker, payload.new_speaker)
    except TranscriptionError as error:
        raise _workflow_error_to_http(
            error,
            not_found_details={"Meeting not found.", "Speaker not found in transcript."},
        ) from error


@router.patch("/segments/{segment_id}", response_model=TranscriptSegment)
async def update_segment(
    meeting_id: str,
    segment_id: str,
    payload: TranscriptSegmentUpdate,
    db: DbSession,
) -> TranscriptSegment:
    try:
        return update_transcript_segment(db, meeting_id, segment_id, payload.text)
    except TranscriptionError as error:
        raise _workflow_error_to_http(
            error,
            not_found_details={"Meeting not found.", "Transcript segment not found."},
        ) from error
