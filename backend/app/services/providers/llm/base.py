from typing import Protocol

from app.schemas.transcript import TranscriptSegment


class LLMProvider(Protocol):
    def generate_meeting_note(self, prompt: str, segments: list[TranscriptSegment]) -> str:
        """Generate Markdown meeting minutes from transcript segments."""
