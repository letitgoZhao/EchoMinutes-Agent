#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT="${ECHOMINUTES_API_PORT:-8765}"

cd "$ROOT_DIR"

echo "Starting EchoMinutes-Agent development services..."
echo "Backend: http://127.0.0.1:${BACKEND_PORT}"
echo "Desktop: Electron/Vue via pnpm"

uv run --project backend uvicorn --app-dir backend app.main:app --reload --host 127.0.0.1 --port "$BACKEND_PORT" &
BACKEND_PID=$!

ECHOMINUTES_SKIP_BACKEND_START=1 corepack pnpm --filter @echominutes/desktop dev &
DESKTOP_PID=$!

trap 'kill "$BACKEND_PID" "$DESKTOP_PID" 2>/dev/null || true' EXIT
wait
