from typing import Protocol

from app.schemas.transcript import TranscriptSegment


class ASRProvider(Protocol):
    def transcribe_placeholder(self) -> list[TranscriptSegment]:
        """Return placeholder transcript segments for P0 development."""
