<div align="center">

# EchoMinutes-Agent

Local-first meeting minutes, from long audio/video to editable notes. ✨

![Electron](https://img.shields.io/badge/Electron-47848F?logo=electron&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-35495E?logo=vuedotjs&logoColor=4FC08D)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-local--first-003B57?logo=sqlite&logoColor=white)
![Qwen](https://img.shields.io/badge/Qwen-DashScope-5C6B73)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

**EchoMinutes-Agent** is an open-source desktop workspace for turning local meeting audio/video into speaker-segmented transcripts, Qwen-style meeting minutes, human-edited Markdown, and Markdown/PDF/Word exports.

```text
local audio/video import
  -> DashScope ASR transcription
  -> Qwen-compatible meeting note generation
  -> transcript and note editing
  -> Markdown / PDF / Word export
  -> local history reuse
```

It is intentionally not a SaaS admin panel. The first version stays focused on a practical local desktop workflow: import, transcribe, generate, edit, export, reopen. Small but useful. 🛠️

## Highlights

- **Desktop-first workflow**: Electron main/preload, Vue renderer, and FastAPI backend stay separated.
- **Real provider path**: DashScope ASR and DashScope-compatible Qwen LLM calls sit behind provider interfaces.
- **Runtime API key settings**: packaged app users can enter DashScope API keys in Settings instead of editing `.env`.
- **Local persistence**: SQLite stores meetings, transcript segments, notes, exports, tasks, and app settings.
- **Review-focused UI**: meeting library, transcript review, note editor, export history, diagnostics, and logs.
- **Export formats**: edited notes can be exported to Markdown, PDF, and Word.
- **Windows packaging path**: a local NSIS installer build is wired through `electron-builder`.

## Quick Links

- **Install, demo, environment, and packaging**: [docs/INSTALL.md](docs/INSTALL.md)
- **Repository structure and module notes**: [docs/STRUCTURE.md](docs/STRUCTURE.md)
- **Agent working contract**: [AGENTS.md](AGENTS.md)
- **Contribution guide**: [CONTRIBUTING.md](CONTRIBUTING.md)

## Current Status

EchoMinutes-Agent is in the **P3 stabilization and packaging slice**:

- P0: runnable Electron/Vue + FastAPI + SQLite skeleton is present.
- P1: import, transcription task records, DashScope ASR path, transcript persistence, retryable task status are wired.
- P2: note model, prompt management, Qwen-compatible note generation, editing, regenerate, and speaker rename are wired.
- P3: Markdown/PDF/Word export, export history, diagnostics, and Windows installer packaging are being hardened.

The Windows installer currently bundles the Electron app plus backend source/lock files and starts the backend with `uv`. That is enough for developer-preview packaging on a machine with `uv` available; a future packaging slice should embed a frozen Python backend binary for non-developer users.

## Minimal Local Run

```powershell
uv sync
corepack pnpm --dir frontend install
.\scripts\dev.ps1
```

Open **Settings** in the app, paste a real DashScope API key, test ASR/LLM readiness, then import a local audio/video file.

## License

MIT License. See [LICENSE](LICENSE).
