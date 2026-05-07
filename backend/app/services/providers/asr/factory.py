from app.core.config import settings
from app.services.providers.asr.base import ASRProvider
from app.services.providers.asr.dashscope import DashScopeASRProvider


def get_asr_provider() -> ASRProvider:
    if not settings.has_dashscope_api_key:
        raise ValueError("DashScope API key is required for transcription.")

    return DashScopeASRProvider(
        api_key=settings.dashscope_api_key,
        model=settings.dashscope_asr_model,
        base_url=settings.dashscope_asr_base_url,
    )
