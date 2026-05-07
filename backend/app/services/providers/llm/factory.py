from app.core.config import settings
from app.services.providers.llm.base import LLMProvider
from app.services.providers.llm.dashscope import DashScopeLLMProvider


def get_llm_provider() -> LLMProvider:
    if not settings.has_dashscope_api_key:
        raise ValueError("DashScope API key is required for meeting note generation.")

    return DashScopeLLMProvider(
        api_key=settings.dashscope_api_key,
        model=settings.dashscope_model,
        base_url=settings.dashscope_base_url,
    )
