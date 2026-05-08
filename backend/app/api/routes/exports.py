from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.export import ExportCreate, ExportResponse
from app.services.workflow.export_service import (
    ExportWorkflowError,
    create_export,
    list_exports,
)

router = APIRouter(prefix="/meetings/{meeting_id}/exports")
DbSession = Annotated[Session, Depends(get_db)]


def _export_error_to_http(error: ExportWorkflowError) -> HTTPException:
    detail = str(error)
    status_code = (
        status.HTTP_404_NOT_FOUND
        if detail == "Meeting not found."
        else status.HTTP_400_BAD_REQUEST
    )
    return HTTPException(status_code=status_code, detail=detail)


@router.get("", response_model=list[ExportResponse])
async def read_exports(meeting_id: str, db: DbSession) -> list[ExportResponse]:
    return list_exports(db, meeting_id)


@router.post("", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def create_export_endpoint(
    meeting_id: str,
    payload: ExportCreate,
    db: DbSession,
) -> ExportResponse:
    try:
        return create_export(db, meeting_id, payload.format)
    except ExportWorkflowError as error:
        raise _export_error_to_http(error) from error
