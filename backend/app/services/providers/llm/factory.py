from app.core.config import settings
from app.services.providers.llm.base import LLMProvider
from app.services.providers.llm.dashscope import DashScopeLLMProvider


def get_llm_provider() -> LLMProvider:
    return get_llm_provider_with_settings(
        api_key=settings.dashscope_api_key,
        model=settings.dashscope_model,
        base_url=settings.dashscope_base_url,
    )


def get_llm_provider_with_settings(
    *,
    api_key: str,
    model: str,
    base_url: str,
) -> LLMProvider:
    if not api_key.strip() or api_key.strip() == "sk-<your_api_key>":
        raise ValueError("DashScope API key is required for meeting note generation.")

    return DashScopeLLMProvider(
        api_key=api_key,
        model=model,
        base_url=base_url,
    )
