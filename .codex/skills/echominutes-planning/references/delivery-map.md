# EchoMinutes Delivery Map

## P0

Minimum runnable monorepo skeleton:

- Electron + Vue 3 + TypeScript + Vite desktop app
- FastAPI backend
- `GET /api/health`
- renderer backend health display
- settings placeholder
- SQLite initialization skeleton
- MockASRProvider and MockLLMProvider
- Windows and Linux development scripts
- Python backend managed with `uv`

## P1

File import and mock transcription:

- Electron file dialog
- Meeting record creation
- copy media into workspace
- transcription task API
- mock speaker-separated segments
- persisted transcript segments
- transcript workspace display
- task status transitions

## P2

Note generation and editing:

- note data model
- summarize API
- standard meeting-note prompt template
- MockLLMProvider fixed Markdown
- note editor
- save edited Markdown
- regenerate note action
- speaker rename support

## P3

Export and stabilization:

- Markdown export
- export record
- PDF export through HTML template
- Word export after PDF is stable
- export history
- open export folder action
