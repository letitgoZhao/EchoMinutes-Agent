import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.transcript import TranscriptSegment  # noqa: E402
from app.services.workflow.media_preprocess_service import PreparedMedia  # noqa: E402


class TestASRProvider:
    def transcribe(self, media_path: str, **_: object) -> list[TranscriptSegment]:
        return [
            TranscriptSegment(
                id="seg-001",
                speaker="Speaker 1",
                start_ms=0,
                end_ms=5200,
                text="Edited planning opened with enterprise deployment readiness.",
                confidence=0.97,
            ),
            TranscriptSegment(
                id="seg-002",
                speaker="Speaker 2",
                start_ms=5300,
                end_ms=10200,
                text="The team agreed to review exports and provider diagnostics.",
                confidence=0.92,
            ),
            TranscriptSegment(
                id="seg-003",
                speaker="Speaker 1",
                start_ms=10400,
                end_ms=15100,
                text="Action items include validating DashScope ASR and Word output.",
                confidence=0.88,
            ),
        ]


class TestLLMProvider:
    def generate_meeting_note(self, prompt: str, segments: list[TranscriptSegment]) -> str:
        speakers = ", ".join(sorted({segment.speaker for segment in segments}))
        return (
            "# Meeting Minutes\n\n"
            "## Summary\n\n"
            f"{segments[0].text}\n\n"
            "## Decisions\n\n"
            "- Use DashScope providers for the production workflow.\n\n"
            "## Action Items\n\n"
            f"- Review speakers: {speakers}.\n"
        )


@pytest.fixture(autouse=True)
def use_test_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.services.workflow.transcription_service.get_asr_provider_with_settings",
        lambda **_: TestASRProvider(),
    )
    monkeypatch.setattr(
        "app.services.workflow.note_service.get_llm_provider_with_settings",
        lambda **_: TestLLMProvider(),
    )
    monkeypatch.setattr(
        "app.api.routes.settings.get_llm_provider_with_settings",
        lambda **_: TestLLMProvider(),
    )
    monkeypatch.setattr(
        "app.services.workflow.transcription_service.prepare_media_for_transcription",
        lambda _meeting_id, media_path: PreparedMedia(
            source_path=Path(media_path).resolve(),
            normalized_path=Path(media_path).resolve(),
            sample_rate_hz=16000,
            format="wav",
            normalized=False,
        ),
    )
