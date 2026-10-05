from fastapi import APIRouter
from ..schemas.traffic import LaneTraffic, TrafficSnapshot
from ai.density.traffic_density import DensityConfig, TrafficDensityEstimator
from ai.signals.adaptive_signal import AdaptiveSignalController

router = APIRouter(prefix="/api/traffic", tags=["traffic"])

_estimator = TrafficDensityEstimator(DensityConfig())
_controller = AdaptiveSignalController()

@router.get("/snapshot", response_model=TrafficSnapshot)
def snapshot():
    counts = {"NORTH": 18, "EAST": 31, "SOUTH": 7, "WEST": 11}
    decision = _controller.decide(counts)
    lanes = [
        LaneTraffic(
            direction=direction,
            vehicle_count=count,
            density=_estimator.classify(count).value,
            signal="GREEN" if direction == decision.direction else "RED",
            remaining_seconds=decision.green_seconds if direction == decision.direction else 24,
        )
        for direction, count in counts.items()
    ]
    return TrafficSnapshot(
        total_vehicles=sum(counts.values()),
        active_direction=decision.direction,
        remaining_seconds=decision.green_seconds,
        lanes=lanes,
    )
