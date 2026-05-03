from app.schemas.transcript import TranscriptSegment


class MockLLMProvider:
    def generate_placeholder_note(self) -> str:
        return """# Meeting Minutes

## Summary

The team aligned on building the P0 EchoMinutes-Agent skeleton before adding real
provider integrations.

## Decisions

- Keep Electron, preload, renderer, and FastAPI responsibilities separate.
- Use mock ASR and mock LLM providers for early development.
- Defer real media import and transcription to P1.

## Action Items

- Verify the backend health endpoint.
- Confirm the settings page can read local development settings.
- Keep provider interfaces stable before adding real DashScope or ASR calls.
"""

    def generate_meeting_note(self, prompt: str, segments: list[TranscriptSegment]) -> str:
        speakers = sorted({segment.speaker for segment in segments})
        first_line = segments[0].text if segments else "No transcript content was available."
        prompt_marker = "Qwen-style" if "Qwen-style" in prompt else "standard"

        return f"""# Meeting Minutes

## Summary

Generated with the mock LLM from {len(segments)} transcript segments using the
{prompt_marker} prompt. The discussion opened with: {first_line}

## Decisions

- Preserve the imported meeting media in the local workspace.
- Keep speaker-separated transcript segments available for review.

## Action Items

- Review speaker labels: {", ".join(speakers) if speakers else "no speakers detected"}.
- Edit this Markdown note before exporting.
"""
