---
name: echominutes-backend
description: Build EchoMinutes-Agent backend code. Use for FastAPI APIs, SQLAlchemy/SQLite persistence, workflow services, ASR/LLM provider abstractions, prompt management, export services, and backend tests.
---

# EchoMinutes Backend

Use this skill for backend implementation in `backend/`.

## Workflow

1. Check the active delivery slice in `AGENTS.md`.
2. Use `uv` for Python dependency management and backend commands.
3. Keep API routers thin and move business logic into services.
4. Put external AI calls behind provider interfaces.
5. Provide mock provider behavior before real provider behavior.
6. Keep prompts centralized, versionable, and away from UI code.
7. Store local state in SQLite through SQLAlchemy.
8. Add focused tests for service behavior when implementation exists.

## Backend Boundaries

- `api/`: FastAPI routers and request/response wiring.
- `services/workflow/`: orchestration of meeting processing steps.
- `services/providers/asr/`: ASR provider interface and implementations.
- `services/providers/llm/`: LLM provider interface and implementations.
- `services/export/`: Markdown, PDF, and Word export logic.
- `models/`: SQLAlchemy persistence models.
- `schemas/`: Pydantic schemas.
- `prompts/`: prompt templates and prompt assembly helpers.

## Provider Rules

- Do not call Aliyun, Qwen, or any cloud API directly from routers.
- Do not require API keys for mock provider flows.
- Never log secrets.
- Return explicit task states and retryable errors.
- Use DashScope compatible-mode settings for early LLM tests:
  - `DASHSCOPE_API_KEY`
  - `DASHSCOPE_BASE_URL`
  - `DASHSCOPE_MODEL`

## References

Load `references/backend-patterns.md` when implementing backend structure or reviewing backend code.
