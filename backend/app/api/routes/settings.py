from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.settings import AppSettings, AppSettingsUpdate
from app.schemas.transcript import TranscriptSegment
from app.services.providers.errors import ProviderRequestError
from app.services.providers.llm.factory import get_llm_provider
from app.services.settings_service import get_app_settings, update_app_settings
from app.services.workflow.media_preprocess_service import get_ffmpeg_path

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
    if not settings.has_dashscope_api_key:
        return {
            "ok": False,
            "provider": "dashscope-compatible",
            "model": settings.dashscope_model,
            "message": "DashScope API key is missing.",
        }

    try:
        provider = get_llm_provider()
        provider.generate_meeting_note(
            prompt=(
                "Return Markdown only:\n"
                "# Meeting Minutes\n\n"
                "## Summary\n\n"
                "Provider readiness check."
            ),
            segments=[
                TranscriptSegment(
                    id="probe-001",
                    speaker="Speaker 1",
                    start_ms=0,
                    end_ms=1000,
                    text="Provider readiness check.",
                    confidence=1.0,
                )
            ],
        )
    except ProviderRequestError as error:
        return {
            "ok": False,
            "provider": "dashscope-compatible",
            "model": settings.dashscope_model,
            "message": f"{error.code}: {error.message}",
        }
    except Exception:
        return {
            "ok": False,
            "provider": "dashscope-compatible",
            "model": settings.dashscope_model,
            "message": "DashScope LLM readiness check failed.",
        }

    return {
        "ok": True,
        "provider": "dashscope-compatible",
        "model": settings.dashscope_model,
        "message": "DashScope LLM readiness check passed.",
    }


@router.post("/settings/test-asr", response_model=dict[str, bool | str])
async def test_asr_settings() -> dict[str, bool | str]:
    ffmpeg_path = get_ffmpeg_path()
    return {
        "ok": settings.has_dashscope_api_key,
        "provider": settings.transcription_provider,
        "model": settings.dashscope_asr_model,
        "ffmpeg": ffmpeg_path or "unavailable",
        "message": (
            "Real transcription is ready."
            if settings.has_dashscope_api_key
            else "DashScope API key is missing."
        ),
    }
