from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import math
import threading

from sqlalchemy import desc

from ..config import settings
from ..database.session import SessionLocal
from ..models.traffic_record import TrafficRecord
from ..schemas.traffic import TrafficSnapshot


LANES = ("NORTH", "EAST", "SOUTH", "WEST")


class TrafficAnalyticsService:
    """Persists throttled traffic samples and computes offline analytics/forecasting."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_record_monotonic: float | None = None

    def record_snapshot(
        self,
        snapshot: TrafficSnapshot,
        *,
        force: bool = False,
        now_monotonic: float | None = None,
    ) -> bool:
        import time

        current = time.monotonic() if now_monotonic is None else now_monotonic
        with self._lock:
            if (
                not force
                and self._last_record_monotonic is not None
                and current - self._last_record_monotonic < max(1, settings.analytics_sample_seconds)
            ):
                return False
            self._last_record_monotonic = current

        lanes = {lane.direction: lane.vehicle_count for lane in snapshot.lanes}
        record = TrafficRecord(
            recorded_at=datetime.now(timezone.utc),
            total_vehicles=snapshot.total_vehicles,
            north_count=lanes.get("NORTH", 0),
            east_count=lanes.get("EAST", 0),
            south_count=lanes.get("SOUTH", 0),
            west_count=lanes.get("WEST", 0),
            active_direction=snapshot.active_direction,
            signal_state=snapshot.signal_state,
            remaining_seconds=snapshot.remaining_seconds,
            green_seconds=snapshot.green_seconds,
            vehicle_type_counts=json.dumps(snapshot.vehicle_type_counts, sort_keys=True),
        )
        with SessionLocal() as db:
            db.add(record)
            db.commit()
        return True

    def history(self, limit: int | None = None) -> list[TrafficRecord]:
        safe_limit = max(1, min(limit or settings.analytics_history_limit, 2000))
        with SessionLocal() as db:
            records = (
                db.query(TrafficRecord)
                .order_by(desc(TrafficRecord.recorded_at), desc(TrafficRecord.id))
                .limit(safe_limit)
                .all()
            )
        records.reverse()
        return records

    def summary(self, limit: int | None = None) -> dict:
        records = self.history(limit)
        if not records:
            return {
                "data_points": 0,
                "average_vehicles": 0.0,
                "peak_vehicles": 0,
                "minimum_vehicles": 0,
                "current_vehicles": 0,
                "busiest_lane": "NORTH",
                "lane_averages": {lane: 0.0 for lane in LANES},
                "signal_state_counts": {},
            }

        lane_values = {
            "NORTH": [r.north_count for r in records],
            "EAST": [r.east_count for r in records],
            "SOUTH": [r.south_count for r in records],
            "WEST": [r.west_count for r in records],
        }
        lane_averages = {
            lane: round(sum(values) / len(values), 2)
            for lane, values in lane_values.items()
        }
        busiest_lane = max(
            LANES,
            key=lambda lane: (lane_averages[lane], -LANES.index(lane)),
        )
        signal_state_counts: dict[str, int] = {}
        for record in records:
            signal_state_counts[record.signal_state] = signal_state_counts.get(record.signal_state, 0) + 1

        totals = [record.total_vehicles for record in records]
        return {
            "data_points": len(records),
            "average_vehicles": round(sum(totals) / len(totals), 2),
            "peak_vehicles": max(totals),
            "minimum_vehicles": min(totals),
            "current_vehicles": totals[-1],
            "busiest_lane": busiest_lane,
            "lane_averages": lane_averages,
            "signal_state_counts": signal_state_counts,
        }

    def predict(self, horizon_minutes: int | None = None, limit: int | None = None) -> dict:
        records = self.history(limit)
        horizon = max(1, min(horizon_minutes or settings.prediction_horizon_minutes, 60))
        if not records:
            return {"data_points": 0, "predictions": []}

        current = float(records[-1].total_vehicles)
        if len(records) == 1:
            method = "current_value_baseline"
            confidence = "LOW"
            predictions = [current for _ in range(horizon)]
        else:
            start = records[0].recorded_at
            xs = [
                max(0.0, (record.recorded_at - start).total_seconds() / 60.0)
                for record in records
            ]
            ys = [float(record.total_vehicles) for record in records]
            slope, intercept = self._linear_fit(xs, ys)

            if len(records) >= 10:
                confidence = "HIGH"
            elif len(records) >= 5:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            predictions = [
                max(0.0, intercept + slope * (xs[-1] + minute))
                for minute in range(1, horizon + 1)
            ]
            method = "linear_trend"

        return {
            "data_points": len(records),
            "predictions": [
                {
                    "horizon_minutes": index,
                    "predicted_total_vehicles": round(value, 2),
                    "confidence": confidence,
                    "method": method,
                }
                for index, value in enumerate(predictions, start=1)
            ],
        }

    @staticmethod
    def _linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        denominator = sum((x - mean_x) ** 2 for x in xs)
        if denominator <= 1e-9:
            return 0.0, mean_y
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x
        return slope, intercept


traffic_analytics = TrafficAnalyticsService()
