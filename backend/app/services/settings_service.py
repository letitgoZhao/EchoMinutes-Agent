from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.setting import Setting
from app.schemas.settings import AppSettings, AppSettingsUpdate
from app.services.workflow.media_preprocess_service import get_ffmpeg_path

SETTING_KEYS = {
    "workspace_dir",
    "dashscope_api_key",
    "dashscope_base_url",
    "dashscope_model",
    "dashscope_asr_base_url",
    "dashscope_asr_model",
    "dashscope_asr_speaker_count",
}


@dataclass(frozen=True)
class ProviderRuntimeSettings:
    dashscope_api_key: str
    dashscope_base_url: str
    dashscope_model: str
    dashscope_asr_base_url: str
    dashscope_asr_model: str
    dashscope_asr_speaker_count: int

    @property
    def has_dashscope_api_key(self) -> bool:
        key = self.dashscope_api_key.strip()
        return bool(key and key != "sk-<your_api_key>")


def _get_value(db: Session, key: str, default: str) -> str:
    setting = db.get(Setting, key)
    return setting.value if setting else default


def _set_value(db: Session, key: str, value: str) -> None:
    setting = db.get(Setting, key)
    if setting:
        setting.value = value
    else:
        db.add(Setting(key=key, value=value))


def _delete_value(db: Session, key: str) -> None:
    setting = db.get(Setting, key)
    if setting:
        db.delete(setting)


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_int(value: int | None) -> str | None:
    if value is None or value < 0:
        return None
    return str(value)


def _get_int_value(db: Session, key: str, default: int) -> int:
    value = _get_value(db, key, str(default))
    try:
        return max(int(value), 0)
    except ValueError:
        return default


def _default_asr_base_url(llm_base_url: str) -> str:
    if settings.dashscope_asr_base_url_raw.strip():
        return settings.dashscope_asr_base_url

    compatible_mode_suffix = "/compatible-mode/v1"
    clean_base_url = llm_base_url.strip().rstrip("/")
    if clean_base_url.endswith(compatible_mode_suffix):
        return f"{clean_base_url[:-len(compatible_mode_suffix)]}/api/v1"

    return "https://dashscope.aliyuncs.com/api/v1"


def get_provider_runtime_settings(db: Session) -> ProviderRuntimeSettings:
    dashscope_base_url = _get_value(
        db,
        "dashscope_base_url",
        settings.dashscope_base_url,
    ).rstrip("/")
    dashscope_asr_base_url = _get_value(
        db,
        "dashscope_asr_base_url",
        _default_asr_base_url(dashscope_base_url),
    ).rstrip("/")
    return ProviderRuntimeSettings(
        dashscope_api_key=_get_value(db, "dashscope_api_key", settings.dashscope_api_key),
        dashscope_base_url=dashscope_base_url,
        dashscope_model=_get_value(db, "dashscope_model", settings.dashscope_model),
        dashscope_asr_base_url=dashscope_asr_base_url,
        dashscope_asr_model=_get_value(
            db,
            "dashscope_asr_model",
            settings.dashscope_asr_model,
        ),
        dashscope_asr_speaker_count=_get_int_value(
            db,
            "dashscope_asr_speaker_count",
            settings.dashscope_asr_speaker_count,
        ),
    )


def get_app_settings(db: Session) -> AppSettings:
    ffmpeg_path = get_ffmpeg_path()
    provider_settings = get_provider_runtime_settings(db)
    return AppSettings(
        api_host=settings.api_host,
        api_port=settings.api_port,
        workspace_dir=_get_value(db, "workspace_dir", str(settings.workspace_dir)),
        transcription_provider=settings.transcription_provider,
        asr_ready=provider_settings.has_dashscope_api_key,
        dashscope_base_url=provider_settings.dashscope_base_url,
        dashscope_model=provider_settings.dashscope_model,
        dashscope_asr_base_url=provider_settings.dashscope_asr_base_url,
        dashscope_asr_model=provider_settings.dashscope_asr_model,
        dashscope_asr_speaker_count=provider_settings.dashscope_asr_speaker_count,
        has_dashscope_api_key=provider_settings.has_dashscope_api_key,
        ffmpeg_available=ffmpeg_path is not None,
        ffmpeg_path=ffmpeg_path,
    )


def update_app_settings(db: Session, payload: AppSettingsUpdate) -> None:
    data = payload.model_dump(exclude_unset=True)
    if data.pop("clear_dashscope_api_key", False):
        _delete_value(db, "dashscope_api_key")

    for key, value in data.items():
        cleaned_value = (
            _clean_int(value)
            if key == "dashscope_asr_speaker_count"
            else _clean_value(value)
        )
        if key in SETTING_KEYS and cleaned_value is not None:
            _set_value(db, key, cleaned_value)
    db.commit()
