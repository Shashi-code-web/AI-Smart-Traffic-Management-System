from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_phase6_analytics_summary_contract():
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200

    payload = response.json()
    assert payload["data_points"] >= 0
    assert payload["average_vehicles"] >= 0
    assert payload["peak_vehicles"] >= 0
    assert set(payload["lane_averages"]) == {"NORTH", "EAST", "SOUTH", "WEST"}


def test_phase6_analytics_history_and_prediction_contract():
    history = client.get("/api/analytics/history?limit=10")
    prediction = client.get("/api/analytics/predict?horizon=3&limit=10")

    assert history.status_code == 200
    assert prediction.status_code == 200
    assert isinstance(history.json(), list)

    payload = prediction.json()
    assert payload["data_points"] >= 0
    assert len(payload["predictions"]) <= 3
    for point in payload["predictions"]:
        assert point["horizon_minutes"] >= 1
        assert point["predicted_total_vehicles"] >= 0
