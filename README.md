<h1 align="center">EchoMinutes-Agent</h1>

<p>
EchoMinutes Agent is a local-first desktop AI meeting-minutes workspace. It turns long local audio or video files into transcripts, Qwen-style meeting notes, editable Markdown, and Markdown/PDF/Word exports.
</p>

<div align="center">
![Electron](https://img.shields.io/badge/Electron-47848F?logo=electron&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue%203-35495E?logo=vuedotjs&logoColor=4FC08D)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-local--first-003B57?logo=sqlite&logoColor=white)
![DashScope](https://img.shields.io/badge/DashScope-ASR%20%2B%20Qwen-5C6B73)
![License](https://img.shields.io/badge/License-MIT-green)
</div>

## What It Does

```text
local audio/video import
  -> DashScope ASR transcription
  -> speaker-aware transcript review
  -> Qwen-compatible meeting note generation
  -> human editing and regeneration
  -> Markdown / PDF / Word export
  -> local history reuse
```

The app is intentionally not a SaaS product. There is no login, payment, admin console, team workspace, or cloud sync in the first version. Your meeting library, notes, exports, logs, and settings are stored locally; only provider calls send media or transcript text to the configured ASR/LLM provider.

## Download

The first public preview is **v0.1.0** for Windows.

- Download the installer from the GitHub Releases page.
- Run `EchoMinutes Agent Setup 0.1.0.exe`.
- Open Settings, enter a DashScope API key, test provider readiness, then import a local audio or video file.

The Windows package includes the Electron desktop app and a bundled FastAPI backend runtime, so normal users do not need to install Python or `uv` just to launch the packaged app.

### Windows Security Notice

Early GitHub Release builds may show a Microsoft Defender SmartScreen or Microsoft Edge warning because the preview installer is new and may be unsigned or low-reputation. Download only from this repository's GitHub Releases page, compare the installer against the published `.sha256` file, then choose **Keep** / **More info** / **Run anyway** only if you trust the source.

Future releases should be code-signed with a stable publisher certificate to reduce these warnings.

## Highlights

- **Local-first desktop workspace**: Electron owns the native shell, Vue owns the renderer UI, FastAPI owns the local workflow API, and SQLite stores local state.
- **Real provider path**: DashScope ASR and DashScope-compatible Qwen note generation are wired through provider abstractions instead of UI-level API calls.
- **Runtime provider settings**: users can configure and test DashScope ASR/LLM readiness inside Settings without editing `.env`.
- **Review-oriented workflow**: meeting library, workflow status, transcript cards, note editor, export actions, and diagnostics are visible in one desktop workspace.
- **Speaker rename and transcript edits**: reviewed transcript changes feed back into regenerated notes.
- **Export pipeline**: edited notes can be exported to Markdown, PDF, and Word, with export history stored locally.
- **Packaged Windows backend**: the release build ships a standalone `backend-runtime/echominutes-backend.exe` and checks backend health through the local API.
- **Diagnostics**: Settings shows host runtime details, provider readiness, FFmpeg availability, backend version, workspace paths, and recent workflow logs.

## Current Status

EchoMinutes-Agent is in the **P3 stabilization and release** slice.

- **P0**: Electron/Vue desktop shell, preload boundary, FastAPI backend, health endpoint, SQLite setup, and settings are in place.
- **P1**: local media import, meeting records, workspace media copies, transcription tasks, DashScope ASR, transcript persistence, retryable failures, and status display are wired.
- **P2**: note model, prompt management, Qwen-compatible generation, note editor, save/regenerate actions, speaker rename, and transcript edit sync are wired.
- **P3**: Markdown/PDF/Word export, export history, local diagnostics, recent logs, and Windows packaging are available and being hardened.

## Provider Setup

EchoMinutes currently targets DashScope-compatible ASR and Qwen-compatible LLM calls.

For the packaged app:

1. Open **Settings**.
2. Enter your DashScope API key.
3. Keep the default Qwen model or update it.
4. Use **Test all providers** before importing a real meeting.

For local development, copy `.env.example` to `.env` and fill only local placeholder values:

```env
DASHSCOPE_API_KEY="sk-<your_api_key>"
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_MODEL="qwen-plus"
DASHSCOPE_ASR_MODEL="paraformer-realtime-v2"
DASHSCOPE_ASR_BASE_URL="https://dashscope.aliyuncs.com/api/v1"
```

Never commit real API keys.

## Local Development

Requirements:

- Windows or Linux development machine
- Python 3.12+
- `uv`
- Node.js 20.20+
- Corepack / pnpm 9.15.0

Install dependencies:

```powershell
uv sync
corepack pnpm@9.15.0 --dir frontend install
```

Run the desktop app in development:

```powershell
.\scripts\dev.ps1
```

Run checks:

```powershell
uv run pytest
corepack pnpm@9.15.0 --dir frontend typecheck
corepack pnpm@9.15.0 --dir frontend build
```

If Windows temp/cache permissions get in the way, keep pytest temp output inside the workspace:

```powershell
$env:UV_CACHE_DIR=".uv-cache-local"
uv run pytest --basetemp .codex\tmp\pytest-basetemp -o cache_dir=.codex\tmp\pytest-cache
```

Build the Windows installer:

```powershell
corepack pnpm@9.15.0 --dir frontend package:win
```

The installer is written to `release/`.

## Repository Structure

```text
backend/             FastAPI app, SQLAlchemy models, workflow services, providers, exports
frontend/            Electron main/preload and Vue renderer app
scripts/             Development, smoke-test, and packaged-backend launcher scripts
docs/                Install, structure, roadmap, and local product notes
workspace.example/   Example local workspace shape
.github/workflows/   CI and Windows packaging workflows
.codex/              Project rules and local agent skills
```

Important files:

- `AGENTS.md`: operating contract for coding agents in this repo.
- `.env.example`: placeholder-only provider and local runtime configuration.
- `pyproject.toml` / `uv.lock`: backend dependency and Python tooling metadata.
- `frontend/package.json`: desktop scripts, Electron Builder config, and Windows packaging inputs.

Generated local files such as `.env`, `.venv/`, `frontend/node_modules/`, `workspace.local/`, `build/`, `dist/`, and `release/` should stay out of Git.

## Privacy Boundary

EchoMinutes is local-first, not fully offline. Local history and generated files stay on your machine, but provider work is explicit:

- imported media may be uploaded to the configured ASR provider;
- transcript text may be sent to the configured LLM provider;
- API keys are local settings and must not be committed;
- logs and errors should not include raw secrets.

## Documentation

- [Install and packaging notes](docs/INSTALL.md)
- [Repository structure](docs/STRUCTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Contribution guide](CONTRIBUTING.md)
- [Agent contract](AGENTS.md)

## License

MIT License. See [LICENSE](LICENSE).
