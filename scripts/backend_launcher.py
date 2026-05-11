from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import uvicorn


def _project_root() -> Path:
    env_root = os.environ.get("ECHOMINUTES_PROJECT_DIR")
    if env_root:
        return Path(env_root).resolve()

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parents[1]

    return Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the EchoMinutes Agent local backend.")
    parser.add_argument("--host", default=os.environ.get("ECHOMINUTES_API_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("ECHOMINUTES_API_PORT", "8765")))
    args = parser.parse_args()

    root = _project_root()
    backend_dir = root / "backend"
    sys.path.insert(0, str(backend_dir))

    os.environ.setdefault("ECHOMINUTES_PROJECT_DIR", str(root))
    from app.main import app

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
