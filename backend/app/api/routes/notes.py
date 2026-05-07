from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.note import NoteResponse, NoteUpdate
from app.services.workflow.note_service import (
    NoteWorkflowError,
    generate_meeting_note,
    get_note,
    save_note,
)

router = APIRouter(prefix="/meetings/{meeting_id}/note")
DbSession = Annotated[Session, Depends(get_db)]


def _note_error_to_http(error: NoteWorkflowError) -> HTTPException:
    detail = str(error)
    status_code = (
        status.HTTP_404_NOT_FOUND
        if detail == "Meeting not found."
        else status.HTTP_400_BAD_REQUEST
    )
    return HTTPException(status_code=status_code, detail=detail)


@router.get("", response_model=NoteResponse | None)
async def read_note(meeting_id: str, db: DbSession) -> NoteResponse | None:
    return get_note(db, meeting_id)


@router.post("/summarize", response_model=NoteResponse)
async def summarize_meeting(meeting_id: str, db: DbSession) -> NoteResponse:
    try:
        return generate_meeting_note(db, meeting_id)
    except NoteWorkflowError as error:
        raise _note_error_to_http(error) from error


@router.put("", response_model=NoteResponse)
async def update_note(meeting_id: str, payload: NoteUpdate, db: DbSession) -> NoteResponse:
    try:
        return save_note(db, meeting_id, payload)
    except NoteWorkflowError as error:
        raise _note_error_to_http(error) from error
