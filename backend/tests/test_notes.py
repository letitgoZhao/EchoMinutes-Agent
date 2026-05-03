from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def _create_transcribed_meeting(client: TestClient, tmp_path: Path) -> dict:
    source_file = tmp_path / "design-review.mp3"
    source_file.write_bytes(b"fake audio data")
    create_response = client.post(
        "/api/meetings",
        json={"source_file_path": str(source_file)},
    )
    meeting = create_response.json()
    client.post(f"/api/meetings/{meeting['id']}/transcribe")
    return meeting


def test_summarize_meeting_persists_mock_note(tmp_path: Path) -> None:
    with TestClient(create_app()) as client:
        meeting = _create_transcribed_meeting(client, tmp_path)
        summarize_response = client.post(f"/api/meetings/{meeting['id']}/note/summarize")
        note_response = client.get(f"/api/meetings/{meeting['id']}/note")

    assert summarize_response.status_code == 200
    note = summarize_response.json()
    assert note["meetingId"] == meeting["id"]
    assert note["markdown"].startswith("# Meeting Minutes")
    assert "mock LLM" in note["markdown"]
    assert note_response.json()["markdown"] == note["markdown"]


def test_summarize_requires_transcript(tmp_path: Path) -> None:
    source_file = tmp_path / "empty-note.wav"
    source_file.write_bytes(b"fake wav data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        response = client.post(f"/api/meetings/{meeting['id']}/note/summarize")

    assert response.status_code == 400
    assert response.json()["detail"] == "Transcript is required before generating a note."


def test_save_note_creates_or_updates_markdown(tmp_path: Path) -> None:
    with TestClient(create_app()) as client:
        meeting = _create_transcribed_meeting(client, tmp_path)
        first_response = client.put(
            f"/api/meetings/{meeting['id']}/note",
            json={"markdown": "# Draft\n\nInitial note."},
        )
        second_response = client.put(
            f"/api/meetings/{meeting['id']}/note",
            json={"markdown": "# Draft\n\nEdited note."},
        )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == second_response.json()["id"]
    assert second_response.json()["markdown"] == "# Draft\n\nEdited note."


def test_summarize_uses_edited_transcript_text(tmp_path: Path) -> None:
    with TestClient(create_app()) as client:
        meeting = _create_transcribed_meeting(client, tmp_path)
        transcript_response = client.get(f"/api/meetings/{meeting['id']}/transcript")
        first_segment = transcript_response.json()[0]
        client.patch(
            f"/api/meetings/{meeting['id']}/segments/{first_segment['id']}",
            json={"text": "Edited transcript opening."},
        )
        summarize_response = client.post(f"/api/meetings/{meeting['id']}/note/summarize")

    assert summarize_response.status_code == 200
    assert "Edited transcript opening." in summarize_response.json()["markdown"]
