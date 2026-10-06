from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_phase5_traffic_snapshot_exposes_safe_signal_state():
    response = client.get("/api/traffic/snapshot")
    assert response.status_code == 200

    payload = response.json()
    assert payload["signal_state"] in {"GREEN", "YELLOW", "ALL_RED"}
    assert payload["remaining_seconds"] >= 0
    assert payload["green_seconds"] >= 1
    assert payload["active_direction"] in {"NORTH", "EAST", "SOUTH", "WEST"}
    assert payload["next_direction"] in {"NORTH", "EAST", "SOUTH", "WEST"}

    green_lanes = [
        lane for lane in payload["lanes"] if lane["signal"] == "GREEN"
    ]
    yellow_lanes = [
        lane for lane in payload["lanes"] if lane["signal"] == "YELLOW"
    ]

    assert len(green_lanes) <= 1
    assert len(yellow_lanes) <= 1

    if payload["signal_state"] == "ALL_RED":
        assert green_lanes == []
        assert yellow_lanes == []
