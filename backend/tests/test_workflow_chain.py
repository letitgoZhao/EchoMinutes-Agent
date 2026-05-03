from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_full_workflow_chain_supports_reopen_and_export_history(tmp_path: Path) -> None:
    source_file = tmp_path / "weekly-review.mp3"
    source_file.write_bytes(b"fake audio data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file), "title": "Weekly Review"},
        )
        meeting = create_response.json()

        transcribe_response = client.post(
            f"/api/meetings/{meeting['id']}/transcription-tasks"
        )
        transcript_response = client.get(f"/api/meetings/{meeting['id']}/transcript")
        transcript = transcript_response.json()
        first_segment = transcript[0]

        rename_response = client.put(
            f"/api/meetings/{meeting['id']}/speakers",
            json={"current_speaker": "Speaker 1", "new_speaker": "Alex"},
        )
        edit_response = client.patch(
            f"/api/meetings/{meeting['id']}/segments/{first_segment['id']}",
            json={"text": "Edited transcript opening."},
        )
        summarize_response = client.post(f"/api/meetings/{meeting['id']}/note/summarize")
        save_response = client.put(
            f"/api/meetings/{meeting['id']}/note",
            json={"markdown": "# Weekly Review\n\nFinal edited note."},
        )
        export_response = client.post(
            f"/api/meetings/{meeting['id']}/exports",
            json={"format": "markdown"},
        )

    assert create_response.status_code == 201
    assert transcribe_response.status_code == 200
    assert rename_response.status_code == 200
    assert any(segment["speaker"] == "Alex" for segment in rename_response.json())
    assert edit_response.status_code == 200
    assert edit_response.json()["text"] == "Edited transcript opening."
    assert summarize_response.status_code == 200
    assert "Edited transcript opening." in summarize_response.json()["markdown"]
    assert save_response.status_code == 200
    assert save_response.json()["markdown"] == "# Weekly Review\n\nFinal edited note."
    assert export_response.status_code == 201

    with TestClient(create_app()) as client:
        meetings_response = client.get("/api/meetings")
        note_response = client.get(f"/api/meetings/{meeting['id']}/note")
        exports_response = client.get(f"/api/meetings/{meeting['id']}/exports")

    assert meetings_response.status_code == 200
    assert any(saved_meeting["id"] == meeting["id"] for saved_meeting in meetings_response.json())
    assert note_response.status_code == 200
    assert note_response.json()["markdown"] == "# Weekly Review\n\nFinal edited note."
    assert exports_response.status_code == 200
    exports = exports_response.json()
    assert len(exports) == 1
    assert exports[0]["format"] == "markdown"
    assert Path(exports[0]["filePath"]).read_text(encoding="utf-8") == (
        "# Weekly Review\n\nFinal edited note."
    )
