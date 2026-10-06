from fastapi.testclient import TestClient

from ai.signals.adaptive_signal import AdaptiveSignalController, SignalConfig
from backend.app.main import app
from backend.app.services.video_validator import inspect_video, resolve_video_path


client = TestClient(app)


def test_phase8_diagnostics_endpoint_has_truthful_checks():
    response = client.get("/api/system/diagnostics")
    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload["healthy"], bool)
    assert {check["name"] for check in payload["checks"]} == {
        "database",
        "video_directory",
        "local_model",
    }
    assert all(isinstance(check["ok"], bool) for check in payload["checks"])


def test_phase8_system_status_reports_database_state():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    payload = response.json()

    assert payload["database_ready"] is True
    assert isinstance(payload["video_ready"], bool)
    assert isinstance(payload["ai_ready"], bool)


def test_phase8_invalid_signal_configuration_fails_fast():
    try:
        AdaptiveSignalController(
            SignalConfig(min_green=10, max_green=5)
        ).decide({"NORTH": 1, "EAST": 0, "SOUTH": 0, "WEST": 0})
    except ValueError as exc:
        assert "max_green" in str(exc)
    else:
        raise AssertionError("Invalid signal configuration was accepted")


def test_phase8_video_validation_rejects_parent_and_absolute_escape():
    for value in ("../../etc/passwd.mp4", "../traffic.mp4"):
        result = inspect_video(value)
        assert result["readable"] is False
        assert "data/videos" in result["error"]

    try:
        resolve_video_path("/tmp/traffic.mp4")
    except ValueError as exc:
        assert "data/videos" in str(exc)
    else:
        raise AssertionError("Absolute path outside data/videos was accepted")
