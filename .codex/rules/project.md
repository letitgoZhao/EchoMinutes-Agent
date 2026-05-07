# EchoMinutes-Agent Project Rules

## Identity

EchoMinutes-Agent is a local-first desktop application for meeting transcription, meeting-note generation, human editing, export, and local history reuse.

## First-Version Boundary

Build the main workflow first:

```text
import media -> transcribe -> structure dialogue -> generate note -> edit -> export -> reopen history
```

Do not start with login, SaaS backend, payment, cloud sync, collaboration, real-time recording, enterprise admin, or packaging polish.

The full product manual is `docs/EchoMinutes-Agent.md` when it exists locally. It is intentionally ignored by git.

## Priority Order

1. P0: runnable desktop/backend skeleton with provider abstractions.
2. P1: local file import and DashScope transcription.
3. P2: note generation, editing, speaker rename, history.
4. P3: export and stability.

## Technical Shape

- Electron owns desktop lifecycle, native dialogs, window management, and starting/stopping local services.
- Preload exposes safe IPC only.
- Vue renderer owns UI state and user workflows.
- FastAPI owns local HTTP APIs and workflow orchestration.
- SQLite stores local state.
- Provider abstractions isolate ASR and LLM implementations.
- DashScope compatible mode is the first LLM test path:
  - `DASHSCOPE_API_KEY`
  - `DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`
  - `DASHSCOPE_MODEL`

## Safety

- Keep secrets out of git.
- Keep tests offline with test doubles; do not keep simulated providers in the product path.
- Cloud provider code must make data transfer explicit and configurable.
- Logs must not include API keys or raw secrets.
