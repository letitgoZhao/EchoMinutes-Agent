# Backend Patterns

## Health

The first API should be:

```http
GET /api/health
```

Expected response:

```json
{
  "ok": true,
  "version": "0.1.0"
}
```

## Suggested API Groups

- Settings: `GET /api/settings`, `PUT /api/settings`, provider test endpoints.
- Meetings: CRUD for local meeting records.
- Transcription: start task, read transcript, update segment.
- Summary: generate, read, and save notes.
- Export: create export and list export history.
- Logs: development-only recent logs.

## Persistence

Keep workspace path and database URL configurable. Avoid hard-coded absolute paths.

## Export Priority

Implement export in this order:

1. Markdown from edited note.
2. PDF through HTML template.
3. Word through structured Markdown or `python-docx`.
