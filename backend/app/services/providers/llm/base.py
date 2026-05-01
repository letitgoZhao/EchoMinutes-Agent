from typing import Protocol


class LLMProvider(Protocol):
    def generate_placeholder_note(self) -> str:
        """Return placeholder Markdown for P0 development."""
