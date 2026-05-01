from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.setting import Setting
from app.schemas.settings import AppSettings, AppSettingsUpdate

SETTING_KEYS = {
    "workspace_dir",
    "dashscope_base_url",
    "dashscope_model",
}


def _get_value(db: Session, key: str, default: str) -> str:
    setting = db.get(Setting, key)
    return setting.value if setting else default


def _set_value(db: Session, key: str, value: str) -> None:
    setting = db.get(Setting, key)
    if setting:
        setting.value = value
    else:
        db.add(Setting(key=key, value=value))


def get_app_settings(db: Session) -> AppSettings:
    return AppSettings(
        api_host=settings.api_host,
        api_port=settings.api_port,
        workspace_dir=_get_value(db, "workspace_dir", str(settings.workspace_dir)),
        dashscope_base_url=_get_value(
            db,
            "dashscope_base_url",
            settings.dashscope_base_url,
        ),
        dashscope_model=_get_value(db, "dashscope_model", settings.dashscope_model),
        has_dashscope_api_key=settings.has_dashscope_api_key,
    )


def update_app_settings(db: Session, payload: AppSettingsUpdate) -> None:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key in SETTING_KEYS and value is not None:
            _set_value(db, key, value)
    db.commit()
