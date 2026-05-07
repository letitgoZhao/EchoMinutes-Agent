from typing import Any, Protocol

from app.schemas.transcript import TranscriptSegment


class ASRProvider(Protocol):
    def transcribe(self, media_path: str, **kwargs: Any) -> list[TranscriptSegment]:
        """Return transcript segments for the provided local media path."""
