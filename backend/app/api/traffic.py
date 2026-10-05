from fastapi import APIRouter

from ..schemas.traffic import LaneTraffic, TrafficSnapshot
from ..services.demo_traffic import DemoTrafficSource

router = APIRouter(prefix="/api/traffic", tags=["traffic"])
_demo = DemoTrafficSource()


@router.get("/snapshot", response_model=TrafficSnapshot)
def snapshot():
    state = _demo.snapshot()
    lanes = [
        LaneTraffic(
            direction=direction,
            vehicle_count=count,
            density=state.densities[direction],
            signal="GREEN" if direction == state.active_direction else "RED",
            remaining_seconds=state.green_seconds if direction == state.active_direction else 24,
        )
        for direction, count in state.counts.items()
    ]
    return TrafficSnapshot(
        total_vehicles=sum(state.counts.values()),
        active_direction=state.active_direction,
        remaining_seconds=state.green_seconds,
        lanes=lanes,
    )
