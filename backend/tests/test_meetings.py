from pathlib import Path

from app.main import create_app
from fastapi.testclient import TestClient


def test_create_meeting_copies_source_media(tmp_path: Path) -> None:
    source_file = tmp_path / "weekly-sync.mp3"
    source_file.write_bytes(b"fake audio data")

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/meetings",
            json={
                "source_file_path": str(source_file),
                "language": "auto",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "weekly-sync"
    assert data["sourceFileName"] == "weekly-sync.mp3"
    assert data["sourceFilePath"] == str(source_file.resolve())
    assert data["status"] == "imported"
    assert Path(data["workspaceMediaPath"]).exists()
    assert Path(data["workspaceMediaPath"]).read_bytes() == b"fake audio data"


def test_list_meetings_includes_created_meeting(tmp_path: Path) -> None:
    source_file = tmp_path / "planning-call.wav"
    source_file.write_bytes(b"fake wav data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={
                "source_file_path": str(source_file),
                "title": "Planning Call",
            },
        )
        list_response = client.get("/api/meetings")

    created = create_response.json()
    assert list_response.status_code == 200
    meeting_ids = {meeting["id"] for meeting in list_response.json()}
    assert created["id"] in meeting_ids


def test_create_meeting_rejects_missing_source_file() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/meetings",
            json={"source_file_path": "D:/does-not-exist/missing.mp3"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Selected media file does not exist."
