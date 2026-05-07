from typing import Any

import httpx

from app.schemas.transcript import TranscriptSegment
from app.services.providers.errors import ProviderRequestError


class DashScopeLLMProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: float = 120.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate_meeting_note(self, prompt: str, segments: list[TranscriptSegment]) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are EchoMinutes Agent. Generate accurate, structured "
                            "Chinese-friendly Markdown meeting minutes from transcripts."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "stream": False,
            },
            timeout=self.timeout_seconds,
        )
        if response.is_error:
            raise _build_provider_error(response)
        payload = response.json()
        markdown = _extract_message_content(payload).strip()
        if not markdown:
            raise ValueError("DashScope returned an empty meeting note.")
        return markdown


def _extract_message_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return ""

    message = first_choice.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                str(part.get("text", ""))
                for part in content
                if isinstance(part, dict)
            )

    text = first_choice.get("text")
    return text if isinstance(text, str) else ""


def _build_provider_error(response: httpx.Response) -> ProviderRequestError:
    code = response.reason_phrase or "RequestFailed"
    message = response.text.strip() or "DashScope LLM request failed."
    try:
        payload = response.json()
    except ValueError:
        payload = {}

    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        code_value = error.get("code") or error.get("type") or code
        message_value = error.get("message") or message
        code = str(code_value)
        message = str(message_value)

    return ProviderRequestError(
        provider="DashScope LLM",
        status_code=response.status_code,
        code=code,
        message=message,
    )
