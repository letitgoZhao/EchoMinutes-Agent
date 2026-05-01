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
