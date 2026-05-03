from collections import deque
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings
from app.schemas.log import LogEntryResponse

LOG_FILE_NAME = "echominutes.log"
LOG_LINE_PARTS = 3


def get_log_file_path() -> Path:
    return settings.workspace_dir / "logs" / LOG_FILE_NAME


def read_recent_logs(limit: int = 50) -> list[LogEntryResponse]:
    if limit < 1:
        return []

    log_path = get_log_file_path()
    if not log_path.exists():
        return []

    recent_lines: deque[str] = deque(maxlen=min(limit, 200))
    for line in log_path.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if stripped_line:
            recent_lines.append(stripped_line)

    entries: list[LogEntryResponse] = []
    for line in reversed(recent_lines):
        entry = _parse_log_line(line)
        if entry is not None:
            entries.append(entry)
    return entries


def _parse_log_line(line: str) -> LogEntryResponse | None:
    parts = line.split(" | ", maxsplit=LOG_LINE_PARTS - 1)
    if len(parts) != LOG_LINE_PARTS:
        return None

    timestamp_text, level, message = parts
    try:
        timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError:
        timestamp = datetime.now(UTC)

    return LogEntryResponse(timestamp=timestamp, level=level, message=message)
