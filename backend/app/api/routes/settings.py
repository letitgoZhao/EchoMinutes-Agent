from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.settings import AppSettings, AppSettingsUpdate
from app.services.settings_service import get_app_settings, update_app_settings

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/settings", response_model=AppSettings)
async def read_settings(db: DbSession) -> AppSettings:
    return get_app_settings(db)


@router.put("/settings", response_model=AppSettings)
async def write_settings(
    payload: AppSettingsUpdate,
    db: DbSession,
) -> AppSettings:
    update_app_settings(db, payload)
    return get_app_settings(db)


@router.post("/settings/test-llm", response_model=dict[str, bool | str])
async def test_llm_settings() -> dict[str, bool | str]:
    return {
        "ok": settings.has_dashscope_api_key,
        "provider": "dashscope-compatible",
        "model": settings.dashscope_model,
    }


@router.post("/settings/test-asr", response_model=dict[str, bool | str])
async def test_asr_settings() -> dict[str, bool | str]:
    return {
        "ok": True,
        "provider": "mock",
        "message": "Real ASR integration starts after the mock workflow is stable.",
    }
