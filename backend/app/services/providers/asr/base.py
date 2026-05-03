from typing import Protocol

from app.schemas.transcript import TranscriptSegment


class ASRProvider(Protocol):
    def transcribe(self, media_path: str) -> list[TranscriptSegment]:
        """Return transcript segments for the provided local media path."""
