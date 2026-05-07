<div align="center">

# EchoMinutes-Agent

![Electron](https://img.shields.io/badge/Electron-47848F?logo=electron&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-35495E?logo=vuedotjs&logoColor=4FC08D)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Qwen](https://img.shields.io/badge/Qwen-LLM-5C6B73)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

**EchoMinutes-Agent** is a local-first, cross-platform desktop client for turning long meeting audio or video into editable, exportable meeting minutes. It is designed as a practical desktop workflow tool, not a SaaS dashboard or account-based collaboration platform.

```text
Import local audio/video
  -> speaker-segmented transcription
  -> AI meeting note generation
  -> human review and editing
  -> Markdown / PDF / Word export
  -> local history reuse
```

## Core Features

- **Local Media Import**: Import local audio or video files from the desktop client.
- **DashScope AI Pipeline**: Run production transcription and note generation through DashScope-backed provider abstractions.
- **Speaker-Segmented Transcript**: Review transcript segments with speaker labels, timestamps, and later manual speaker renaming.
- **Qwen-Style Note Generation**: Use DashScope compatible mode for real Qwen meeting-note generation.
- **Editable Meeting Minutes**: Generate structured Markdown notes and let users review, revise, and save them locally.
- **Export Pipeline**: Export edited notes to Markdown first, then PDF, then Word.
- **Local-First Workspace**: Store settings, transcript data, notes, export records, and history in a local workspace.

## Quick Start

This repository now contains the desktop workflow shell and real-provider backend path: an Electron/Vue renderer, a local FastAPI backend, health/settings endpoints, SQLite persistence, DashScope ASR/LLM providers, export services, and a lightweight Chinese/English UI switch.

### Prerequisites

- **Python**: `3.11+`
- **uv**: Python dependency and environment management
- **Node.js**: `18+`
- **pnpm**: frontend and Electron workspace package manager

### Local Configuration

Copy the example environment file and fill in a test API key only when real DashScope-compatible calls are needed:

```powershell
Copy-Item .env.example .env
```

Current `.env` shape:

```env
ECHOMINUTES_ENV="development"
ECHOMINUTES_API_HOST="127.0.0.1"
ECHOMINUTES_API_PORT="8765"
ECHOMINUTES_WORKSPACE_DIR="./workspace.local"
DASHSCOPE_API_KEY="sk-<your_api_key>"
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_MODEL="qwen-plus"
DASHSCOPE_ASR_BASE_URL="https://dashscope.aliyuncs.com/api/v1"
DASHSCOPE_ASR_MODEL="paraformer-realtime-v2"
ECHOMINUTES_FFMPEG_PATH=""
```

Real user keys should eventually be entered through the desktop settings UI. `.env` is only for local development and must never be committed.

### Run Locally

After installing dependencies, start the development workflow:

```powershell
uv sync
corepack pnpm --dir frontend install
.\scripts\dev.ps1
```

Or start services manually:

```powershell
uv run uvicorn --app-dir backend app.main:app --reload --host 127.0.0.1 --port 8765
corepack pnpm --dir frontend dev
```

## Planned Architecture

```text
Electron desktop shell
  -> safe preload IPC
  -> Vue renderer
  -> local FastAPI backend
  -> SQLite workspace
  -> ASR / LLM providers
  -> Markdown / PDF / Word exporters
```

## Expected Project Structure

The expected structure is shown at directory level. Only special project files and key configuration files are listed explicitly.

```text
echominutes-agent/
  .codex/
  frontend/
    package.json
    pnpm-lock.yaml
    pnpm-workspace.yaml
    electron.vite.config.ts
    tsconfig.json
    electron/
    renderer/
  backend/
    app/
    tests/
  docs/
    EchoMinutes-Agent.md
  scripts/
    dev.ps1
    dev.sh
  workspace.example/
  .editorconfig
  .env.example
  .gitattributes
  .gitignore
  AGENTS.md
  CONTRIBUTING.md
  LICENSE
  pyproject.toml
  README.md
  uv.lock
```

## Delivery Roadmap

- **P0**: Electron + Vue skeleton, FastAPI health endpoint, SQLite skeleton, settings, development scripts.
- **P1**: local file import, meeting record creation, DashScope transcription task flow, transcript segment persistence and display.
- **P2**: Qwen-style meeting note generation, Markdown note editor, speaker rename, history reopen.
- **P3**: Markdown/PDF/Word export, export history, error handling, diagnostics, and validation after the core flow is stable.

## First-Version Non-Goals

- No login, payment, SaaS admin, or cloud sync.
- No online collaboration.
- No real-time recording in the first version.
- No automatic real-name speaker identification.
- No direct cloud API calls scattered inside UI or business logic.
- No packaging polish before the core import-to-export workflow works.

## Documentation

- Product and delivery manual: [docs/EchoMinutes-Agent.md](docs/EchoMinutes-Agent.md)
- Agent development rules: [AGENTS.md](AGENTS.md)
- Codex project rules: [.codex/rules/project.md](.codex/rules/project.md)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License. See [LICENSE](LICENSE).
