---
name: echominutes-desktop-ui
description: Build EchoMinutes-Agent desktop frontend work. Use for Electron main/preload, Vue renderer, IPC, local backend health display, meeting workspace UX, settings, import flow, transcript review, note editor, and export UI.
---

# EchoMinutes Desktop UI

Use this skill for Electron and Vue work under `apps/desktop/`.

## Workflow

1. Keep Electron main, preload, and renderer responsibilities separate.
2. Put native dialogs, service lifecycle, and filesystem access behind safe preload APIs.
3. Route backend calls through a shared renderer API client.
4. Build a practical desktop workspace, not a landing page.
5. Keep UI states visible: backend status, workflow step, task status, errors, and retry actions.

## Main Workspace Shape

The primary screen should support repeated review work:

- top: app title, current status, settings entry
- left: meeting library or workflow stepper
- center: transcript conversation
- right: note editor and export actions
- bottom: media progress and current task state

## UI Priorities

- Import local media.
- Show processing status.
- Display transcript cards with speaker label and timestamps.
- Allow speaker rename.
- Generate, edit, save, and regenerate Markdown notes.
- Export Markdown first, then PDF and Word.

## References

Load `references/ui-patterns.md` when implementing or reviewing desktop UI structure.
