from app.core.config import settings
from app.services.providers.asr.base import ASRProvider
from app.services.providers.asr.dashscope import DashScopeASRProvider


def get_asr_provider() -> ASRProvider:
    return get_asr_provider_with_settings(
        api_key=settings.dashscope_api_key,
        model=settings.dashscope_asr_model,
        base_url=settings.dashscope_asr_base_url,
        speaker_count=settings.dashscope_asr_speaker_count,
    )


def get_asr_provider_with_settings(
    *,
    api_key: str,
    model: str,
    base_url: str,
    speaker_count: int = 0,
) -> ASRProvider:
    if not api_key.strip() or api_key.strip() == "sk-<your_api_key>":
        raise ValueError("DashScope API key is required for transcription.")

    return DashScopeASRProvider(
        api_key=api_key,
        model=model,
        base_url=base_url,
        speaker_count=speaker_count,
    )
