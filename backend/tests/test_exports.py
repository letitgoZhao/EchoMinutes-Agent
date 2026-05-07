from pathlib import Path
from zipfile import ZipFile

from app.main import create_app
from fastapi.testclient import TestClient


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
        json={
            "markdown": (
                "# Export Review\n\n"
                "Ready to export.\n\n"
                "## Decisions\n\n"
                "- Ship structured exports.\n"
                "1. Validate generated files."
            )
        },
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
        == "# Export Review\n\n"
        "Ready to export.\n\n"
        "## Decisions\n\n"
        "- Ship structured exports.\n"
        "1. Validate generated files."
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
    pdf_bytes = Path(export["filePath"]).read_bytes()
    assert pdf_bytes.startswith(b"%PDF-1.4")
    assert b"/Info" in pdf_bytes
    assert b"EchoMinutes Agent" in pdf_bytes


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
    with ZipFile(export["filePath"]) as docx:
        names = set(docx.namelist())
        document_xml = docx.read("word/document.xml").decode("utf-8")

    assert "word/styles.xml" in names
    assert "word/numbering.xml" in names
    assert "docProps/core.xml" in names
    assert 'w:pStyle w:val="Heading1"' in document_xml
    assert 'w:numId w:val="1"' in document_xml
    assert 'w:numId w:val="2"' in document_xml


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
