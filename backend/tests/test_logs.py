from pathlib import Path
from uuid import uuid4

from app.main import create_app
from fastapi.testclient import TestClient


def test_recent_logs_endpoint_returns_startup_entry() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/logs/recent")

    assert response.status_code == 200
    entries = response.json()
    assert any(entry["message"] == "Application startup complete." for entry in entries)


def test_recent_logs_include_workflow_events() -> None:
    source_dir = Path("workspace.local") / "test-inputs"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_file = source_dir / f"workflow-log-{uuid4().hex}.mp3"
    source_file.write_bytes(b"fake audio data")

    with TestClient(create_app()) as client:
        meeting_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = meeting_response.json()
        client.post(f"/api/meetings/{meeting['id']}/transcription-tasks")
        client.post(f"/api/meetings/{meeting['id']}/note/summarize")
        client.post(
            f"/api/meetings/{meeting['id']}/exports",
            json={"format": "markdown"},
        )
        logs_response = client.get("/api/logs/recent?limit=50")

    assert logs_response.status_code == 200
    messages = [entry["message"] for entry in logs_response.json()]
    assert any("Imported meeting media" in message for message in messages)
    assert any("Completed transcription" in message for message in messages)
    assert any("Generated meeting note" in message for message in messages)
    assert any("Created export" in message for message in messages)
