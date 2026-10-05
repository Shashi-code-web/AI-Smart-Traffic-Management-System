from fastapi import APIRouter

from ..schemas.traffic import LaneTraffic, TrafficSnapshot
from ..services.demo_traffic import DemoTrafficSource
from ..services.video_runtime import video_runtime

router = APIRouter(prefix="/api/traffic", tags=["traffic"])
_demo = DemoTrafficSource()


def _from_live(pipeline):
    return TrafficSnapshot(
        total_vehicles=pipeline.current_vehicle_count,
        active_direction=pipeline.active_direction,
        remaining_seconds=pipeline.green_seconds,
        lanes=[
            LaneTraffic(
                direction=direction,
                vehicle_count=count,
                density=pipeline.lane_densities[direction],
                signal="GREEN" if direction == pipeline.active_direction else "RED",
                remaining_seconds=pipeline.green_seconds if direction == pipeline.active_direction else 24,
            )
            for direction, count in pipeline.lane_counts.items()
        ],
    )


@router.get("/snapshot", response_model=TrafficSnapshot)
def snapshot():
    session = video_runtime.status()
    live = video_runtime.snapshot()
    if session.running and session.mode == "AI_VIDEO" and live is not None:
        return _from_live(live)

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
