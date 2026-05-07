from collections.abc import Iterable
from http import HTTPStatus
from pathlib import Path
from typing import Any

import dashscope
from dashscope.audio.asr import Recognition, RecognitionCallback

from app.schemas.transcript import TranscriptSegment
from app.services.providers.errors import ProviderRequestError


class DashScopeASRProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        speaker_count: int = 0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.speaker_count = max(speaker_count, 0)

    def transcribe(
        self,
        media_path: str,
        *,
        media_format: str = "wav",
        sample_rate_hz: int = 16000,
    ) -> list[TranscriptSegment]:
        dashscope.api_key = self.api_key
        dashscope.base_http_api_url = self.base_url

        recognition = Recognition(
            model=self.model,
            callback=RecognitionCallback(),
            format=media_format,
            sample_rate=sample_rate_hz,
            diarization_enabled=True,
            speaker_count=self.speaker_count or None,
            semantic_punctuation_enabled=True,
            timestamp_alignment_enabled=True,
        )
        result = recognition.call(
            str(Path(media_path).resolve()),
        )
        if result.status_code != HTTPStatus.OK:
            code = result.code or "RequestFailed"
            message = result.message or result.code or "DashScope ASR request failed."
            raise ProviderRequestError(
                provider="DashScope ASR",
                status_code=int(result.status_code) if result.status_code else None,
                code=str(code),
                message=str(message),
            )
        sentences = result.get_sentence()
        return _map_sentences_to_segments(sentences)


def _map_sentences_to_segments(sentences: Any) -> list[TranscriptSegment]:
    if isinstance(sentences, dict):
        sentence_items = [sentences]
    elif isinstance(sentences, Iterable):
        sentence_items = [item for item in sentences if isinstance(item, dict)]
    else:
        sentence_items = []

    segments: list[TranscriptSegment] = []
    for index, sentence in enumerate(sentence_items, start=1):
        text = str(
            sentence.get("text")
            or sentence.get("sentence")
            or sentence.get("transcript")
            or ""
        ).strip()
        if not text:
            continue

        start_ms = _as_int(
            sentence.get("begin_time")
            or sentence.get("beginTime")
            or sentence.get("start_time")
            or sentence.get("startTime")
        )
        end_ms = _as_int(
            sentence.get("end_time")
            or sentence.get("endTime")
            or sentence.get("stop_time")
            or sentence.get("stopTime")
        )
        confidence = _as_confidence(
            sentence.get("confidence")
            or sentence.get("sentence_confidence")
            or sentence.get("score")
        )
        speaker_label = _speaker_label(
            sentence.get("speaker_id")
            or sentence.get("speakerId")
            or sentence.get("speaker")
            or sentence.get("channel_id")
            or sentence.get("channelId")
        )

        segments.append(
            TranscriptSegment(
                id=f"seg-{index:03d}",
                speaker=speaker_label,
                start_ms=start_ms,
                end_ms=max(end_ms, start_ms + 1),
                text=text,
                confidence=confidence,
            )
        )

    if segments:
        return segments

    raw_text = ""
    if isinstance(sentences, dict):
        raw_text = str(sentences.get("text") or sentences.get("sentence") or "").strip()
    if raw_text:
        return [
            TranscriptSegment(
                id="seg-001",
                speaker="Speaker 1",
                start_ms=0,
                end_ms=1,
                text=raw_text,
                confidence=0.9,
            )
        ]

    raise ValueError("DashScope returned no transcript segments.")


def _as_int(value: Any) -> int:
    try:
        return max(int(float(value)), 0)
    except (TypeError, ValueError):
        return 0


def _as_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.9
    return min(max(confidence, 0.0), 1.0)


def _speaker_label(value: Any) -> str:
    try:
        speaker_number = int(value)
    except (TypeError, ValueError):
        return "Speaker 1"
    return f"Speaker {speaker_number + 1}"
