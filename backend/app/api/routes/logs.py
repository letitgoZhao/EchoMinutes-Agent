from fastapi import APIRouter, Query

from app.schemas.log import LogEntryResponse
from app.services.log_service import read_recent_logs

router = APIRouter(prefix="/logs")


@router.get("/recent", response_model=list[LogEntryResponse])
async def read_logs_recent(limit: int = Query(default=50, ge=1, le=200)) -> list[LogEntryResponse]:
    return read_recent_logs(limit=limit)
