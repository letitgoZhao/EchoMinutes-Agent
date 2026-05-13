# Repository Structure

Tree-style overview of EchoMinutes-Agent after the project layout refactor. This file stays under |docs/| so the repository root can stay tidy.

```text
EchoMinutes-Agent/
|-- .codex/
|   |-- rules/                         # Project rules for coding agents
|   |-- skills/                        # Project-local Codex skills
|-- .github/
|   |-- workflows/                     # CI and Windows package workflows
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   |-- router.py              # Main API router
|   |   |   |-- routes/                # Thin FastAPI route modules
|   |   |-- core/
|   |   |   |-- config.py              # Env-backed development defaults
|   |   |-- db/
|   |   |   |-- base.py                # SQLAlchemy declarative base
|   |   |   |-- init_db.py             # SQLite table creation
|   |   |   |-- session.py             # Engine and session factory
|   |   |-- models/                    # SQLAlchemy persistence records
|   |   |-- prompts/
|   |   |   |-- meeting_note.py        # Meeting-note prompt assembly
|   |   |-- schemas/                   # Pydantic request/response contracts
|   |   |-- services/
|   |   |   |-- export/                # Markdown, PDF, Word exporters
|   |   |   |-- providers/
|   |   |   |   |-- asr/               # DashScope ASR provider abstraction
|   |   |   |   |-- llm/               # DashScope-compatible LLM provider
|   |   |   |-- workflow/              # Meeting import/transcribe/note/export logic
|   |   |   |-- log_service.py         # Recent local log reader
|   |   |   |-- settings_service.py    # Runtime settings and provider config
|   |   |-- utils/
|   |   |   |-- logging.py             # Rotating local workflow logs
|   |   |-- main.py                    # FastAPI app factory
|   |-- tests/
|       |-- manual/
|       |   |-- real_e2e_smoke.py      # Real provider import-to-export smoke run
|       |-- ...                        # Offline backend regression tests
|-- docs/
|   |-- INSTALL.md                     # Setup, demo, env, and packaging guide
|   |-- STRUCTURE.md                   # This file
|-- frontend/
|   |-- electron/
|   |   |-- main/
|   |   |   |-- index.ts               # Electron lifecycle, backend spawn, dialogs
|   |   |-- preload/
|   |       |-- index.ts               # Safe IPC bridge for renderer
|   |-- renderer/
|   |   |-- index.html
|   |   |-- src/
|   |       |-- app/                   # Vue app bootstrap and shell
|   |       |-- components/            # Workspace, transcript, note, theme UI
|   |       |-- pages/                 # Workspace and Settings pages
|   |       |-- router/                # Vue Router setup
|   |       |-- services/              # Shared API and desktop clients
|   |       |-- stores/                # Pinia state for workflow/settings/theme/i18n
|   |       |-- styles/                # Global desktop UI tokens and layout
|   |-- electron.vite.config.ts        # Electron/Vite build config
|   |-- package.json                   # Desktop scripts and electron-builder config
|   |-- pnpm-lock.yaml                 # Frontend dependency lockfile
|   |-- pnpm-workspace.yaml
|   |-- tsconfig.json
|-- scripts/
|   |-- dev.ps1                        # Windows dev launcher
|   |-- dev.sh                         # Linux/macOS-style dev launcher
|-- workspace.example/
|   |-- README.md                      # Local workspace placeholder
|-- AGENTS.md                          # AI coding agent operating contract
|-- CONTRIBUTING.md
|-- LICENSE
|-- README.md                          # Open-source project overview
|-- pyproject.toml                     # Backend dependencies/tooling
|-- pytest.ini
|-- uv.lock                            # Backend dependency lockfile
```

## Functional Notes

- **Electron main** owns desktop lifecycle, native file dialogs, export-folder opening, and local backend startup.
- **Preload** exposes safe desktop APIs; the Vue renderer does not touch Node filesystem APIs directly.
- **Renderer services** are the only frontend layer that calls backend HTTP APIs.
- **Settings page** saves runtime DashScope settings to local SQLite so packaged app users do not need to edit |.env|.
- **FastAPI routes** stay thin and delegate workflow behavior to backend services.
- **Provider factories** isolate DashScope ASR and DashScope-compatible LLM creation.
- **Workflow services** orchestrate import, transcription, note generation, editing, speaker rename, and export.
- **Export services** keep Markdown, PDF, and Word generation separate from note/transcription logic.
- **SQLite workspace** stores local meetings, transcript segments, notes, export records, processing tasks, settings, and logs.

## Generated And Local-Only Paths

These paths are intentionally ignored and can be cleaned when they are only cache/output data:

```text
.env
.venv/
.pytest_cache/
.ruff_cache/
pytest-cache-files-*/
backend/.pytest-temp/
backend/.runtime-workspace/
backend/.uv-cache-local/
frontend/out/
release/
workspace.local/
*.sqlite3
logs/
wav/
```

Real API keys, imported media, generated exports, and local databases must stay out of git.
