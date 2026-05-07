# Install, Demo, And Windows Packaging

This guide is the practical path for running EchoMinutes-Agent locally, testing real DashScope/Qwen settings, and building a Windows installer.

## Prerequisites

- Windows 10/11 for the current packaging path.
- Python 3.11+.
- `uv` for backend dependency management.
- Node.js 18+.
- Corepack-enabled `pnpm`.
- A DashScope API key for real ASR and Qwen-compatible note generation.

## First Clone Setup

From the repository root:

```powershell
uv sync
corepack pnpm --dir frontend install
```

Optional development `.env`:

```powershell
Copy-Item .env.example .env
```

`.env` is only for development defaults. For packaged app usage, open **Settings** in the desktop app and paste the real DashScope API key there instead.

## Local Development Run

Start both backend and desktop app:

```powershell
.\scripts\dev.ps1
```

Manual split-terminal mode:

```powershell
uv run uvicorn --app-dir backend app.main:app --reload --host 127.0.0.1 --port 8765
```

```powershell
$env:ECHOMINUTES_SKIP_BACKEND_START="1"
corepack pnpm --dir frontend dev
```

## Quick Demo Flow

1. Open **Settings**.
2. Paste a real `DASHSCOPE_API_KEY`.
3. Keep the default LLM base URL unless you need another compatible endpoint:
   `https://dashscope.aliyuncs.com/compatible-mode/v1`
4. Keep the default LLM model unless you need another Qwen-compatible model:
   `qwen-plus`
5. Confirm ASR model:
   `paraformer-realtime-v2`
6. Optional: set **ASR Speaker Count Hint**. Use `0` for auto, or a known meeting size such as `4` when the provider needs help separating speakers.
7. Click the ASR and LLM readiness tests.
8. Go to **Workspace** and import a local audio/video file.
9. Run DashScope ASR.
10. Review speaker-separated transcript segments.
11. Generate meeting notes.
12. Edit the transcript or note if needed.
13. Export Markdown, PDF, or Word.
14. Open the export folder from the export history.

## Runtime Provider Settings

Settings entered in the app are saved in local SQLite under the configured workspace. The app does not return the saved API key to the UI after saving; it only reports whether a real key is configured.

Recommended packaged-app path:

```text
install app
  -> open Settings
  -> paste real DashScope API key
  -> test ASR / LLM readiness
  -> run the meeting workflow
```

## Validation Commands

Backend:

```powershell
uv run --project backend pytest
uv run --project backend ruff check backend
```

Frontend:

```powershell
corepack pnpm --dir frontend typecheck
corepack pnpm --dir frontend build
```

Real long-audio end-to-end smoke:

```powershell
uv run --project backend python backend\tests\manual\real_e2e_smoke.py wav\ami_meeting_10min.wav --sync-env-provider-settings
```

If the provider returns only one speaker for a known multi-speaker meeting, pass a speaker-count hint:

```powershell
uv run --project backend python backend\tests\manual\real_e2e_smoke.py wav\ami_meeting_10min.wav --sync-env-provider-settings --speaker-count-hint 4
```

When Windows user-directory permissions block `uv` or Corepack caches, use project-local cache folders:

```powershell
$env:UV_CACHE_DIR="$PWD\.cache\uv"
$env:COREPACK_HOME="$PWD\.cache\corepack"
```

## Build A Windows Installer

The current package script builds an NSIS installer:

```powershell
corepack pnpm --dir frontend package:win
```

Expected output:

```text
release/
  EchoMinutes Agent Setup <version>.exe
  latest.yml
```

Current packaging boundary:

- The installer bundles the Electron app, backend source, `pyproject.toml`, `uv.lock`, and `.env.example`.
- The installed app starts the local FastAPI backend through `uv`.
- For this developer-preview package, `uv` must be available on the Windows machine.
- A later release-quality packaging slice should freeze the backend into a standalone executable and remove the runtime `uv` requirement.

## GitHub Actions

Two workflows are provided:

- `CI`: runs backend tests plus frontend typecheck/build on pushes and pull requests.
- `Package Windows`: manually triggered workflow that builds the Windows installer and uploads the `release/` files as artifacts.

For open-source contributors, this means a fresh clone can run checks and produce a Windows build from GitHub Actions without committing local secrets. Real API keys are still entered at runtime in the app Settings page.
