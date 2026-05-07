# AGENTS.md

This file is the operating contract for AI coding agents working on EchoMinutes-Agent.

## Product North Star

EchoMinutes-Agent is a local-first, cross-platform desktop workspace for turning long meeting audio or video files into structured, editable, exportable meeting minutes.

The first version must stay focused on:

```text
local audio/video import
  -> speaker-segmented transcription
  -> Qwen-style meeting note generation
  -> human editing
  -> Markdown / PDF / Word export
  -> local history reuse
```

## Required Reading

At the start of each task:

1. Read this file.
2. Read `docs/EchoMinutes-Agent.md` when it exists locally. This product manual is local-only and intentionally ignored by git.
3. Check `.codex/rules/project.md` and any relevant rule file in `.codex/rules/`.
4. Inspect the current repository structure and code before making assumptions.
5. Identify the active delivery slice: P0, P1, P2, or P3.

If documentation conflicts with current code, treat current code as the implementation reality. If the user gives a newer explicit instruction, follow the user's instruction.

## Delivery Slices

P0: create the minimum runnable monorepo skeleton.

- Electron main process, preload, and Vue renderer.
- FastAPI backend with `GET /api/health`.
- Renderer displays backend connection status.
- Basic settings page with local settings.
- SQLite initialization skeleton with SQLAlchemy.
- DashScope ASR and DashScope-compatible LLM providers behind abstractions.
- Windows and Linux development scripts.

P1: implement file import and DashScope transcription.

- Use Electron file dialog for audio/video selection.
- Create meeting records.
- Copy imported media to the local workspace.
- Add transcription task APIs.
- Persist and display speaker-separated transcript segments.
- Show task status transitions and retryable failures.

P2: implement meeting note generation and editing.

- Add note model and summarize API.
- Add prompt templates.
- Use DashScope-compatible LLM provider for production note generation.
- Add note editor and save edited Markdown.
- Add regenerate note action.
- Add speaker rename support.

P3: implement export and stabilization.

- Export edited note to Markdown.
- Add export records and history.
- Add PDF export after Markdown is stable.
- Add Word export after PDF is stable.
- Add open export folder action.
- Improve logs, errors, and packaging only after the core flow works.

## Architecture Rules

- Keep Electron main, preload, renderer, and FastAPI responsibilities separate.
- Renderer code must not directly access Node filesystem APIs.
- Expose native desktop capabilities through preload IPC.
- All frontend backend calls must go through a shared API client.
- Do not hard-code backend URLs in components.
- Keep backend layers separated: API, service, provider, model, schema, prompt, export.
- All ASR and LLM calls must go through provider abstractions.
- Keep prompts under backend prompt management, not in UI components.
- Keep tests offline with test doubles, but do not keep simulated providers in the product path.
- Use `path.join` in Node and `pathlib` in Python for paths.
- Keep local workspace paths configurable.
- Use `uv` for Python dependency management and backend commands.

## Security And Privacy

- Never commit real API keys or secrets.
- Never log API keys.
- Error messages must not leak secrets.
- `.env` is local only; `.env.example` documents the same variables with placeholder values.
- Early development should keep `.env` concise: DashScope compatible-mode API key/base URL, model name, and essential local development settings.
- Make cloud processing explicit in settings: media may go to ASR providers and transcript text may go to LLM providers.
- Do not add account, login, payment, SaaS admin, or cloud sync features in the first version.

## UI Rules

- Build a dense, work-focused desktop tool, not a marketing landing page.
- Prioritize the meeting library, workflow status, transcript review, note editor, export actions, and settings.
- Keep the main workspace suitable for repeated review work:
  - left: meeting library or workflow steps
  - center: transcript
  - right: note editor
  - bottom: media progress and task status
- Prefer clear controls and predictable navigation over decorative UI.
- Speaker cards must show speaker name, timestamp range, text, and low-confidence hints when available.

## Coding Discipline

- Keep changes scoped to the requested task and active delivery slice.
- Prefer existing patterns once the project has code.
- Add abstractions only when they support provider swapping, workflow clarity, or meaningful reuse.
- Do not do unrelated refactors.
- Do not introduce heavy UI frameworks unless explicitly justified.
- Keep real Aliyun or Qwen calls behind provider/service interfaces.

## Validation

After code changes, run at least one relevant check when available:

- Frontend typecheck.
- Frontend lint.
- Backend pytest.
- Backend startup or health endpoint check.
- Local end-to-end manual flow.

If a check cannot be run because the project is not scaffolded yet or dependencies are missing, state that clearly.

## Final Response Checklist

At the end of each task, report:

- What changed.
- Which files changed.
- What validation ran.
- Remaining risks or TODOs.
- Suggested next task.
