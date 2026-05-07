import wave
from pathlib import Path

import pytest
from app.services.workflow.media_preprocess_service import (
    MediaPreparationError,
    prepare_media_for_transcription,
)


def test_prepare_wave_media_uses_local_file_without_ffmpeg(tmp_path: Path) -> None:
    source_file = tmp_path / "sample.wav"
    with wave.open(str(source_file), "wb") as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(16000)
        wave_file.writeframes(b"\x00\x00" * 160)

    prepared = prepare_media_for_transcription("meeting-001", str(source_file))

    assert prepared.normalized_path == source_file.resolve()
    assert prepared.sample_rate_hz == 16000
    assert prepared.normalized is False


def test_prepare_non_wave_media_requires_ffmpeg(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "sample.mp4"
    source_file.write_bytes(b"fake video data")
    monkeypatch.setattr(
        "app.services.workflow.media_preprocess_service.get_ffmpeg_path",
        lambda: None,
    )

    with pytest.raises(MediaPreparationError, match="FFmpeg"):
        prepare_media_for_transcription("meeting-002", str(source_file))
