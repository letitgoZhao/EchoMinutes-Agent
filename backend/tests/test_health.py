from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["version"] == "0.1.0"
    assert data["workspaceDir"]


def test_settings_endpoint_reads_local_defaults() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/settings")

    assert response.status_code == 200
    data = response.json()
    assert data["apiHost"] == "127.0.0.1"
    assert data["apiPort"] == 8765
    assert data["workspaceDir"]
    assert data["dashscopeBaseUrl"]
    assert data["dashscopeModel"]
    assert isinstance(data["hasDashscopeApiKey"], bool)


def test_settings_endpoint_updates_safe_local_values() -> None:
    with TestClient(create_app()) as client:
        response = client.put(
            "/api/settings",
            json={
                "workspace_dir": "./workspace.local",
                "dashscope_model": "qwen-plus",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["workspaceDir"]
    assert data["dashscopeModel"] == "qwen-plus"


def test_mock_transcript_endpoint_returns_speaker_segments() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/dev/mock/transcript")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    first_segment = data[0]
    assert first_segment["speaker"].startswith("Speaker")
    assert first_segment["startMs"] < first_segment["endMs"]
    assert first_segment["text"]
    assert 0 <= first_segment["confidence"] <= 1


def test_mock_note_endpoint_returns_markdown() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/dev/mock/note")

    assert response.status_code == 200
    data = response.json()
    assert data["markdown"].startswith("# Meeting Minutes")
