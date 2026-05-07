from http import HTTPStatus
from types import SimpleNamespace

import httpx
import pytest
from app.schemas.transcript import TranscriptSegment
from app.services.providers.asr.dashscope import _map_sentences_to_segments
from app.services.providers.errors import ProviderRequestError
from app.services.providers.llm.dashscope import DashScopeLLMProvider


def test_dashscope_asr_maps_sentence_payload_to_segments() -> None:
    segments = _map_sentences_to_segments(
        [
            {
                "text": "Discuss enterprise transcription.",
                "begin_time": 100,
                "end_time": 1800,
                "speaker_id": 0,
                "confidence": 0.93,
            },
            {
                "sentence": "Confirm PDF and Word exports.",
                "beginTime": 1900,
                "endTime": 3200,
                "speakerId": 1,
                "score": 0.88,
            },
        ]
    )

    assert [segment.speaker for segment in segments] == ["Speaker 1", "Speaker 2"]
    assert segments[0].text == "Discuss enterprise transcription."
    assert segments[1].start_ms == 1900
    assert segments[1].confidence == 0.88


def test_dashscope_asr_rejects_empty_sentence_payload() -> None:
    with pytest.raises(ValueError, match="no transcript"):
        _map_sentences_to_segments([])


def test_dashscope_llm_provider_reads_chat_completion(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_post(
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, object],
        timeout: float,
    ) -> SimpleNamespace:
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return SimpleNamespace(
            is_error=False,
            json=lambda: {
                "choices": [
                    {"message": {"content": "# Meeting Minutes\n\n## Summary\n\nDone."}}
                ]
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = DashScopeLLMProvider(
        api_key="sk-test",
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    markdown = provider.generate_meeting_note(
        prompt="Write notes.",
        segments=[
            TranscriptSegment(
                id="seg-001",
                speaker="Speaker 1",
                start_ms=0,
                end_ms=1,
                text="Hello",
                confidence=0.9,
            )
        ],
    )

    assert markdown.startswith("# Meeting Minutes")
    assert captured["url"] == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    assert captured["headers"] == {
        "Authorization": "Bearer sk-test",
        "Content-Type": "application/json",
    }
    assert captured["timeout"] == 120.0


def test_dashscope_llm_provider_surfaces_dashscope_error_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error_response = httpx.Response(
        HTTPStatus.FORBIDDEN,
        json={
            "error": {
                "code": "AllocationQuota.FreeTierOnly",
                "message": "The free tier of the model has been exhausted.",
            }
        },
    )

    def fake_post(*_: object, **__: object) -> SimpleNamespace:
        return SimpleNamespace(
            is_error=True,
            status_code=error_response.status_code,
            reason_phrase=error_response.reason_phrase,
            text=error_response.text,
            json=error_response.json,
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = DashScopeLLMProvider(
        api_key="bad-key",
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    with pytest.raises(ProviderRequestError, match="AllocationQuota.FreeTierOnly"):
        provider.generate_meeting_note(prompt="Write notes.", segments=[])
