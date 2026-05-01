# EchoMinutes-Agent Codex Workspace

This directory stores project-specific Codex guidance and reusable skills.

## Contents

- `rules/`: concise project rules that future AI coding agents should read before implementation.
- `skills/`: project-local skills for planning, backend work, and desktop UI work.

These files are intentionally committed so future coding sessions inherit the same product boundaries and engineering habits.

## Project Skills

- `echominutes-planning`: scope work against P0/P1/P2/P3.
- `echominutes-backend`: EchoMinutes FastAPI, workflow, provider, persistence, and export guidance.
- `echominutes-desktop-ui`: EchoMinutes Electron/Vue desktop guidance.
- `python-patterns`: general Python style and idioms.
- `fastapi-patterns`: general FastAPI patterns.
- `vue-best-practices`: general Vue guidance.
- `vue-router-best-practices`: Vue Router guidance.

## Using Local Skills Later

The skills under `.codex/skills` are project assets. If you want Codex to auto-discover them globally, copy or install the selected skill folders into your Codex skills directory. Until then, reference them by path when needed.
