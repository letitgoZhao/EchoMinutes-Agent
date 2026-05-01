# Development Rules

## Before Editing

- Read `AGENTS.md`.
- Read `docs/EchoMinutes-Agent.md`.
- Inspect the current code and project structure.
- Identify the active delivery slice.
- Keep the task small enough to verify.

## Frontend

- Use a shared API client for backend calls.
- Keep backend URLs configurable.
- Keep filesystem and native desktop access behind preload IPC.
- Use Pinia for cross-page workflow state once state becomes complex.
- Keep components split between pages, reusable components, services, stores, and styles.

## Backend

- Use `uv` for Python dependency and command execution.
- Keep API routers thin.
- Put workflow logic in services.
- Keep ASR and LLM calls behind provider interfaces.
- Keep prompts centralized under backend prompt management.
- Use SQLAlchemy models and Pydantic schemas deliberately.
- Keep export code isolated from transcription and summarization services.

## Verification

Run the narrowest meaningful check after each change. Prefer `uv run pytest`, `uv run ruff check .`, and focused backend startup checks once backend code exists. If the repo is still unscaffolded, document that validation is limited to file inspection.
