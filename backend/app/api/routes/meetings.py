from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.services.workflow.meeting_service import (
    MeetingImportError,
    create_meeting_from_source,
    get_meeting,
    list_meetings,
)

router = APIRouter(prefix="/meetings")
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[MeetingResponse])
async def read_meetings(db: DbSession) -> list[MeetingResponse]:
    return list_meetings(db)


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(payload: MeetingCreate, db: DbSession) -> MeetingResponse:
    try:
        return create_meeting_from_source(db, payload)
    except MeetingImportError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def read_meeting(meeting_id: str, db: DbSession) -> MeetingResponse:
    meeting = get_meeting(db, meeting_id)
    if meeting is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found.")
    return meeting
