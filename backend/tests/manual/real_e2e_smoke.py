# ruff: noqa: E402, I001

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.schemas.meeting import MeetingCreate
from app.schemas.settings import AppSettingsUpdate
from app.services.settings_service import get_provider_runtime_settings, update_app_settings
from app.services.workflow.export_service import create_export
from app.services.workflow.meeting_service import create_meeting_from_source
from app.services.workflow.note_service import generate_meeting_note
from app.services.workflow.transcription_service import (
    create_transcription_task,
    get_transcript_segments,
    run_transcription_task,
)

EXPORT_FORMATS = ("markdown", "pdf", "word")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the real EchoMinutes flow: import media, transcribe with DashScope, "
            "generate Qwen-compatible notes, and export Markdown/PDF/Word."
        )
    )
    parser.add_argument(
        "media_path",
        type=Path,
        help="Local audio/video file to use for the real end-to-end smoke run.",
    )
    parser.add_argument(
        "--title",
        default="EchoMinutes real API smoke",
        help="Meeting title to save in the local workspace.",
    )
    parser.add_argument(
        "--language",
        default="auto",
        help="Meeting language hint saved with the meeting record.",
    )
    parser.add_argument(
        "--accent-hint",
        default=None,
        help="Optional accent hint saved with the meeting record.",
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        choices=EXPORT_FORMATS,
        default=list(EXPORT_FORMATS),
        help="Export formats to create after note generation.",
    )
    parser.add_argument(
        "--speaker-count-hint",
        type=int,
        default=None,
        help="Optional speaker count hint for DashScope diarization. Use 0 for auto.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=None,
        help="Optional path for the JSON smoke report.",
    )
    parser.add_argument(
        "--sync-env-provider-settings",
        action="store_true",
        help=(
            "Copy provider settings from .env into local runtime settings before the run. "
            "Useful after UI tests or manual probes changed the SQLite settings table."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_path = args.media_path.expanduser().resolve()
    if not source_path.exists() or not source_path.is_file():
        print(json.dumps({"ok": False, "error": "media file not found"}, ensure_ascii=False))
        return 2

    init_db()
    started = perf_counter()

    with SessionLocal() as db:
        if args.sync_env_provider_settings:
            update_app_settings(
                db,
                AppSettingsUpdate(
                    dashscope_api_key=settings.dashscope_api_key,
                    dashscope_base_url=settings.dashscope_base_url,
                    dashscope_model=settings.dashscope_model,
                    dashscope_asr_base_url=settings.dashscope_asr_base_url,
                    dashscope_asr_model=settings.dashscope_asr_model,
                    dashscope_asr_speaker_count=settings.dashscope_asr_speaker_count,
                ),
            )
        if args.speaker_count_hint is not None:
            update_app_settings(
                db,
                AppSettingsUpdate(
                    dashscope_asr_speaker_count=max(args.speaker_count_hint, 0),
                ),
            )

        provider_settings = get_provider_runtime_settings(db)
        if not provider_settings.has_dashscope_api_key:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "DashScope API key is not configured.",
                        "workspaceDir": str(settings.workspace_dir),
                    },
                    ensure_ascii=False,
                )
            )
            return 2

        meeting = create_meeting_from_source(
            db,
            MeetingCreate(
                source_file_path=str(source_path),
                title=args.title,
                language=args.language,
                accent_hint=args.accent_hint,
            ),
        )
        task = create_transcription_task(db, meeting.id)
        transcribed_meeting = run_transcription_task(db, task)
        segments = get_transcript_segments(db, meeting.id)
        note = generate_meeting_note(db, meeting.id)
        exports = [create_export(db, meeting.id, export_format) for export_format in args.formats]

        report = {
            "ok": True,
            "createdAt": datetime.now(UTC).isoformat(),
            "durationSeconds": round(perf_counter() - started, 2),
            "workspaceDir": str(settings.workspace_dir),
            "meeting": {
                "id": meeting.id,
                "title": meeting.title,
                "status": transcribed_meeting.status,
                "sourceFileName": meeting.source_file_name,
                "workspaceMediaPath": meeting.workspace_media_path,
            },
            "transcriptionTask": {
                "id": task.id,
                "status": task.status,
                "attemptCount": task.attempt_count,
                "retryable": task.retryable,
            },
            "provider": {
                "asrModel": provider_settings.dashscope_asr_model,
                "asrSpeakerCountHint": provider_settings.dashscope_asr_speaker_count,
                "llmModel": provider_settings.dashscope_model,
            },
            "transcript": {
                "segmentCount": len(segments),
                "speakerCount": len({segment.speaker for segment in segments}),
                "firstSegmentPreview": segments[0].text[:160] if segments else "",
            },
            "note": {
                "id": note.id,
                "markdownLength": len(note.markdown),
                "startsWithHeading": note.markdown.lstrip().startswith("#"),
            },
            "exports": [
                {
                    "id": export.id,
                    "format": export.format,
                    "filePath": export.file_path,
                    "exists": Path(export.file_path).exists(),
                    "bytes": Path(export.file_path).stat().st_size
                    if Path(export.file_path).exists()
                    else 0,
                }
                for export in exports
            ],
        }

    report_path = args.report_path
    if report_path is None:
        report_dir = settings.workspace_dir / "e2e"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"real-e2e-{datetime.now(UTC):%Y%m%d-%H%M%S}.json"
    else:
        report_path = report_path.expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["reportPath"] = str(report_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
