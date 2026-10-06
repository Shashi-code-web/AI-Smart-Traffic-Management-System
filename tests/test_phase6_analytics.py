from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.session import Base
from backend.app.models.traffic_record import TrafficRecord
from backend.app.services import traffic_analytics as analytics_module
from backend.app.services.traffic_analytics import TrafficAnalyticsService


def _service_with_temp_db(monkeypatch):
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(analytics_module, "SessionLocal", Session)
    service = TrafficAnalyticsService()
    return service, Session, engine


def _insert_points(Session):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with Session() as db:
        for index, total in enumerate((10, 15, 20, 25, 30)):
            db.add(
                TrafficRecord(
                    recorded_at=start + timedelta(minutes=index),
                    total_vehicles=total,
                    north_count=total,
                    east_count=2,
                    south_count=1,
                    west_count=1,
                    active_direction="NORTH",
                    signal_state="GREEN",
                    remaining_seconds=15,
                    green_seconds=25,
                    vehicle_type_counts="{}",
                )
            )
        db.commit()


def test_phase6_summary_calculates_peak_average_and_busiest_lane(monkeypatch):
    service, Session, engine = _service_with_temp_db(monkeypatch)
    try:
        _insert_points(Session)
        summary = service.summary()

        assert summary["data_points"] == 5
        assert summary["average_vehicles"] == 20.0
        assert summary["peak_vehicles"] == 30
        assert summary["minimum_vehicles"] == 10
        assert summary["current_vehicles"] == 30
        assert summary["busiest_lane"] == "NORTH"
        assert summary["lane_averages"]["NORTH"] == 20.0
        assert summary["signal_state_counts"] == {"GREEN": 5}
    finally:
        engine.dispose()


def test_phase6_prediction_follows_positive_traffic_trend(monkeypatch):
    service, Session, engine = _service_with_temp_db(monkeypatch)
    try:
        _insert_points(Session)
        prediction = service.predict(horizon_minutes=3)

        assert prediction["data_points"] == 5
        assert prediction["predictions"][0]["predicted_total_vehicles"] == 35.0
        assert prediction["predictions"][-1]["predicted_total_vehicles"] == 45.0
        assert prediction["predictions"][0]["method"] == "linear_trend"
        assert prediction["predictions"][0]["confidence"] == "MEDIUM"
    finally:
        engine.dispose()


def test_phase6_record_snapshot_is_throttled(monkeypatch):
    service, Session, engine = _service_with_temp_db(monkeypatch)
    try:
        from backend.app.schemas.traffic import LaneTraffic, TrafficSnapshot

        snapshot = TrafficSnapshot(
            total_vehicles=12,
            vehicle_type_counts={"car": 8},
            active_direction="NORTH",
            next_direction="EAST",
            signal_state="GREEN",
            remaining_seconds=12,
            green_seconds=20,
            signal_reason="test",
            lanes=[
                LaneTraffic(
                    direction=direction,
                    vehicle_count=12 if direction == "NORTH" else 0,
                    density="MEDIUM" if direction == "NORTH" else "LOW",
                    signal="GREEN" if direction == "NORTH" else "RED",
                    remaining_seconds=12 if direction == "NORTH" else 0,
                )
                for direction in ("NORTH", "EAST", "SOUTH", "WEST")
            ],
        )

        assert service.record_snapshot(snapshot, now_monotonic=0.0, force=True) is True
        assert service.record_snapshot(snapshot, now_monotonic=2.0) is False
        assert service.record_snapshot(snapshot, now_monotonic=5.0) is True
        assert len(service.history()) == 2
    finally:
        engine.dispose()
