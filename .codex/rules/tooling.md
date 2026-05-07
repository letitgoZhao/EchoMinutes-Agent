# Tooling Rules

## Python

- Use `uv` for backend Python dependency management and command execution.
- Keep Python configuration in the repository root `pyproject.toml`; backend source stays under `backend/`.
- Commit `uv.lock` once dependencies are resolved by the project.
- Prefer `uv run pytest`, `uv run ruff check .`, and `uv run pyright` or equivalent type checks when configured.

## JavaScript

- Use `pnpm` for the Electron/Vue workspace unless the project later chooses otherwise.
- Keep frontend package files under `frontend/` and run frontend commands with `corepack pnpm --dir frontend ...` from the repository root.
- Keep package scripts focused on common workflows: dev, build, typecheck, lint, test.

## Environment

- Keep `.env` and `.env.example` aligned by variable name.
- Never commit real `DASHSCOPE_API_KEY` values.
