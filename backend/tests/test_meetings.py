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


def test_delete_meeting_soft_deletes_record_and_keeps_media(tmp_path: Path) -> None:
    source_file = tmp_path / "delete-review.wav"
    source_file.write_bytes(b"keep this media")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file), "title": "Delete Review"},
        )
        meeting = create_response.json()
        copied_media_path = Path(meeting["workspaceMediaPath"])

        delete_response = client.delete(f"/api/meetings/{meeting['id']}")
        read_response = client.get(f"/api/meetings/{meeting['id']}")
        list_response = client.get("/api/meetings")

    assert delete_response.status_code == 204
    assert read_response.status_code == 404
    assert meeting["id"] not in {item["id"] for item in list_response.json()}
    assert copied_media_path.exists()
    assert copied_media_path.read_bytes() == b"keep this media"


def test_delete_meeting_returns_not_found_for_missing_meeting() -> None:
    with TestClient(create_app()) as client:
        response = client.delete("/api/meetings/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting not found."


def test_create_meeting_rejects_missing_source_file() -> None:
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/meetings",
            json={"source_file_path": "D:/does-not-exist/missing.mp3"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Selected media file does not exist."
