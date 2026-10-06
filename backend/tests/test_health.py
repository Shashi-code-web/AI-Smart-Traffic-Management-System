from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "0.6.0"


def test_system_status():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    assert response.json()["mode"] == "demo"


def test_root_reports_phase_six():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["phase"] == 6
