from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def _create_meeting_with_note(client: TestClient, tmp_path: Path) -> dict:
    source_file = tmp_path / "export-review.mp3"
    source_file.write_bytes(b"fake audio data")
    create_response = client.post(
        "/api/meetings",
        json={"source_file_path": str(source_file), "title": "Export Review"},
    )
    meeting = create_response.json()
    client.put(
        f"/api/meetings/{meeting['id']}/note",
        json={"markdown": "# Export Review\n\nReady to export."},
    )
    return meeting


def test_markdown_export_writes_file_and_records_history(tmp_path: Path) -> None:
    with TestClient(create_app()) as client:
        meeting = _create_meeting_with_note(client, tmp_path)
        export_response = client.post(
            f"/api/meetings/{meeting['id']}/exports",
            json={"format": "markdown"},
        )
        history_response = client.get(f"/api/meetings/{meeting['id']}/exports")

    assert export_response.status_code == 201
    export = export_response.json()
    assert export["format"] == "markdown"
    assert export["fileName"].endswith(".md")
    assert (
        Path(export["filePath"]).read_text(encoding="utf-8")
        == "# Export Review\n\nReady to export."
    )

    assert history_response.status_code == 200
    assert history_response.json()[0]["id"] == export["id"]


def test_pdf_export_writes_pdf_file(tmp_path: Path) -> None:
    with TestClient(create_app()) as client:
        meeting = _create_meeting_with_note(client, tmp_path)
        export_response = client.post(
            f"/api/meetings/{meeting['id']}/exports",
            json={"format": "pdf"},
        )

    assert export_response.status_code == 201
    export = export_response.json()
    assert export["format"] == "pdf"
    assert export["fileName"].endswith(".pdf")
    assert Path(export["filePath"]).read_bytes().startswith(b"%PDF-1.4")


def test_word_export_writes_docx_file(tmp_path: Path) -> None:
    with TestClient(create_app()) as client:
        meeting = _create_meeting_with_note(client, tmp_path)
        export_response = client.post(
            f"/api/meetings/{meeting['id']}/exports",
            json={"format": "word"},
        )

    assert export_response.status_code == 201
    export = export_response.json()
    assert export["format"] == "word"
    assert export["fileName"].endswith(".docx")
    assert Path(export["filePath"]).read_bytes().startswith(b"PK")


def test_markdown_export_requires_saved_note(tmp_path: Path) -> None:
    source_file = tmp_path / "missing-note.mp3"
    source_file.write_bytes(b"fake audio data")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/meetings",
            json={"source_file_path": str(source_file)},
        )
        meeting = create_response.json()
        response = client.post(
            f"/api/meetings/{meeting['id']}/exports",
            json={"format": "markdown"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "A saved note is required before export."
