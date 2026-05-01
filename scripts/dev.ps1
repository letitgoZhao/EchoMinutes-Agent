param(
    [int]$BackendPort = 8765
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Starting EchoMinutes-Agent development services..."
Write-Host "Backend: http://127.0.0.1:$BackendPort"
Write-Host "Desktop: Electron/Vue via pnpm"

$backendCommand = "uv run --project backend uvicorn --app-dir backend app.main:app --reload --host 127.0.0.1 --port $BackendPort"
$desktopCommand = "`$env:ECHOMINUTES_SKIP_BACKEND_START='1'; corepack pnpm --filter @echominutes/desktop dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WorkingDirectory $root
Start-Process powershell -ArgumentList "-NoExit", "-Command", $desktopCommand -WorkingDirectory $root
