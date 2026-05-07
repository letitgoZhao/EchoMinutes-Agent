from pathlib import Path

from app.main import create_app
from fastapi.testclient import TestClient


def test_transcribe_meeting_persists_segments_and_updates_status(tmp_path: Path) -> None:
    source_file = tmp_path / "retrospective.mp4"
    source_file.write_bytes(b"fake video data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()

        transcribe_response = client.post(f"/api/meetings/{meeting['id']}/transcribe")
        transcript_response = client.get(f"/api/meetings/{meeting['id']}/transcript")

    assert transcribe_response.status_code == 200
    transcribed_meeting = transcribe_response.json()
    assert transcribed_meeting["status"] == "transcribed"

    assert transcript_response.status_code == 200
    transcript = transcript_response.json()
    assert len(transcript) == 3
    assert transcript[0]["speaker"] == "Speaker 1"
    assert transcript[0]["startMs"] == 0
    assert transcript[0]["endMs"] > transcript[0]["startMs"]

    with TestClient(create_app()) as client:
        task_response = client.get(f"/api/meetings/{meeting['id']}/transcription-tasks")

    assert task_response.status_code == 200
    tasks = task_response.json()
    assert tasks[0]["kind"] == "transcription"
    assert tasks[0]["status"] == "succeeded"
    assert tasks[0]["retryable"] is False


def test_transcript_endpoint_returns_empty_list_before_transcription(tmp_path: Path) -> None:
    source_file = tmp_path / "roadmap.wav"
    source_file.write_bytes(b"fake wav data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        transcript_response = client.get(f"/api/meetings/{meeting['id']}/transcript")

    assert transcript_response.status_code == 200
    assert transcript_response.json() == []


def test_transcribe_missing_meeting_returns_404() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/meetings/missing-meeting/transcribe")

    assert response.status_code == 404
    assert response.json()["detail"] == "Meeting not found."


def test_rename_speaker_updates_matching_segments(tmp_path: Path) -> None:
    source_file = tmp_path / "rename-speaker.mp4"
    source_file.write_bytes(b"fake video data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        client.post(f"/api/meetings/{meeting['id']}/transcribe")
        response = client.put(
            f"/api/meetings/{meeting['id']}/speakers",
            json={"current_speaker": "Speaker 1", "new_speaker": "Alice"},
        )

    assert response.status_code == 200
    transcript = response.json()
    assert transcript[0]["speaker"] == "Alice"
    assert any(segment["speaker"] == "Speaker 2" for segment in transcript)


def test_update_transcript_segment_persists_edited_text(tmp_path: Path) -> None:
    source_file = tmp_path / "edit-transcript.mp3"
    source_file.write_bytes(b"fake audio data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        client.post(f"/api/meetings/{meeting['id']}/transcribe")
        transcript_response = client.get(f"/api/meetings/{meeting['id']}/transcript")
        first_segment = transcript_response.json()[0]

        update_response = client.patch(
            f"/api/meetings/{meeting['id']}/segments/{first_segment['id']}",
            json={"text": "Edited transcript opening."},
        )
        refreshed_transcript_response = client.get(f"/api/meetings/{meeting['id']}/transcript")

    assert update_response.status_code == 200
    assert update_response.json()["text"] == "Edited transcript opening."
    assert refreshed_transcript_response.json()[0]["text"] == "Edited transcript opening."


def test_start_transcription_task_returns_task_and_meeting(tmp_path: Path) -> None:
    source_file = tmp_path / "task-start.mp4"
    source_file.write_bytes(b"fake video data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        response = client.post(f"/api/meetings/{meeting['id']}/transcription-tasks")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task"]["status"] == "succeeded"
    assert payload["task"]["attemptCount"] == 1
    assert payload["meeting"]["status"] == "transcribed"


def test_retry_missing_transcription_task_returns_404(tmp_path: Path) -> None:
    source_file = tmp_path / "task-retry.wav"
    source_file.write_bytes(b"fake wav data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        response = client.post(
            f"/api/meetings/{meeting['id']}/transcription-tasks/missing-task/retry"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transcription task not found."


def test_update_missing_transcript_segment_returns_404(tmp_path: Path) -> None:
    source_file = tmp_path / "missing-segment.wav"
    source_file.write_bytes(b"fake wav data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        client.post(f"/api/meetings/{meeting['id']}/transcribe")
        response = client.patch(
            f"/api/meetings/{meeting['id']}/segments/missing-segment",
            json={"text": "Edited transcript opening."},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transcript segment not found."
