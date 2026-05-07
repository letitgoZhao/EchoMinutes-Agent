from app.main import create_app
from fastapi.testclient import TestClient


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
    assert data["transcriptionProvider"] == "dashscope"
    assert isinstance(data["asrReady"], bool)
    assert data["dashscopeBaseUrl"]
    assert data["dashscopeModel"]
    assert data["dashscopeAsrBaseUrl"]
    assert data["dashscopeAsrModel"]
    assert isinstance(data["hasDashscopeApiKey"], bool)
    assert isinstance(data["ffmpegAvailable"], bool)


def test_settings_endpoint_updates_safe_local_values() -> None:
    with TestClient(create_app()) as client:
        response = client.put(
            "/api/settings",
            json={
                "workspace_dir": "./workspace.local",
                "dashscope_model": "qwen-plus",
                "dashscope_asr_model": "paraformer-realtime-v2",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["workspaceDir"]
    assert data["dashscopeModel"] == "qwen-plus"


def test_asr_settings_endpoint_reports_dashscope_readiness() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/settings/test-asr")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["ok"], bool)
    assert data["provider"] == "dashscope"


def test_llm_settings_endpoint_runs_provider_probe() -> None:
    with TestClient(create_app()) as client:
        client.put("/api/settings", json={"dashscope_api_key": "sk-test"})
        response = client.post("/api/settings/test-llm")
        client.put("/api/settings", json={"clear_dashscope_api_key": True})

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["provider"] == "dashscope-compatible"
