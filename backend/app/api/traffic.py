from fastapi import APIRouter

from ..schemas.traffic import LaneTraffic, TrafficSnapshot
from ..services.demo_traffic import DemoTrafficSource
from ..services.traffic_analytics import traffic_analytics
from ..services.video_runtime import video_runtime

router = APIRouter(prefix="/api/traffic", tags=["traffic"])
_demo = DemoTrafficSource()


def _lane_signal(direction: str, active_direction: str, signal_state: str) -> str:
    if signal_state == "ALL_RED":
        return "RED"
    if direction != active_direction:
        return "RED"
    return signal_state


def _from_live(pipeline) -> TrafficSnapshot:
    return TrafficSnapshot(
        total_vehicles=pipeline.current_vehicle_count,
        vehicle_type_counts=pipeline.vehicle_type_counts,
        active_direction=pipeline.active_direction,
        next_direction=pipeline.next_direction,
        signal_state=pipeline.signal_state,
        remaining_seconds=pipeline.remaining_seconds,
        green_seconds=pipeline.green_seconds,
        signal_reason=pipeline.signal_reason,
        lanes=[
            LaneTraffic(
                direction=direction,
                vehicle_count=count,
                density=pipeline.lane_densities[direction],
                signal=_lane_signal(
                    direction,
                    pipeline.active_direction,
                    pipeline.signal_state,
                ),
                remaining_seconds=(
                    pipeline.remaining_seconds
                    if direction == pipeline.active_direction
                    else 0
                ),
            )
            for direction, count in pipeline.lane_counts.items()
        ],
    )


@router.get("/snapshot", response_model=TrafficSnapshot)
def snapshot():
    session = video_runtime.status()
    live = video_runtime.snapshot()
    if session.mode == "AI_VIDEO" and live is not None:
        result = _from_live(live)
    else:
        state = _demo.snapshot()
        result = TrafficSnapshot(
            total_vehicles=sum(state.counts.values()),
            vehicle_type_counts={},
            active_direction=state.active_direction,
            next_direction=state.next_direction,
            signal_state=state.signal_state,
            remaining_seconds=state.remaining_seconds,
            green_seconds=state.green_seconds,
            signal_reason=state.signal_reason,
            lanes=[
                LaneTraffic(
                    direction=direction,
                    vehicle_count=count,
                    density=state.densities[direction],
                    signal=_lane_signal(
                        direction,
                        state.active_direction,
                        state.signal_state,
                    ),
                    remaining_seconds=(
                        state.remaining_seconds
                        if direction == state.active_direction
                        else 0
                    ),
                )
                for direction, count in state.counts.items()
            ],
        )

    traffic_analytics.record_snapshot(result)
    return result
