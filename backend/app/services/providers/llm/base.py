from typing import Protocol

from app.schemas.transcript import TranscriptSegment


class LLMProvider(Protocol):
    def generate_placeholder_note(self) -> str:
        """Return placeholder Markdown for P0 development."""

    def generate_meeting_note(self, prompt: str, segments: list[TranscriptSegment]) -> str:
        """Generate Markdown meeting minutes from transcript segments."""
