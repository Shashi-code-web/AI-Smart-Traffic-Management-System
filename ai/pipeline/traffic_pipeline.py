from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ai.counting.vehicle_counter import VehicleCounter
from ai.density.traffic_density import DensityConfig, TrafficDensityEstimator
from ai.detection.vehicle_detector import Detection, VehicleDetector
from ai.lane.lane_mapper import Lane, LaneMapper
from ai.signals.adaptive_signal import AdaptiveSignalController, SignalConfig, SignalState


@dataclass(frozen=True)
class PipelineSnapshot:
    total_tracked: int
    current_vehicle_count: int
    vehicle_type_counts: dict[str, int]
    lane_counts: dict[str, int]
    lane_densities: dict[str, str]
    active_direction: str
    next_direction: str
    signal_state: str
    remaining_seconds: int
    green_seconds: int
    model_ready: bool
    signal_reason: str
    processed_at: str


class TrafficPipeline:
    """Processes consecutive frames with local YOLO + ByteTrack and converts them to traffic state."""

    def __init__(
        self,
        model_path: str,
        confidence: float = 0.35,
        density_config: DensityConfig | None = None,
        signal_config: SignalConfig | None = None,
    ) -> None:
        self.detector = VehicleDetector(model_path, confidence)
        self.tracker_counter = VehicleCounter()
        self.density = TrafficDensityEstimator(density_config)
        self.signal = AdaptiveSignalController(signal_config)
        self.lane_mapper = LaneMapper()
        self.last_detections: list[Detection] = []
        self._last = self._empty_snapshot()

    def _empty_snapshot(self) -> PipelineSnapshot:
        counts = {lane.value: 0 for lane in Lane}
        signal = self.signal.reset(direction=Lane.NORTH.value, now=0.0)
        return PipelineSnapshot(
            total_tracked=0,
            current_vehicle_count=0,
            vehicle_type_counts={},
            lane_counts=counts,
            lane_densities={lane: self.density.classify(0).value for lane in counts},
            active_direction=signal.direction,
            next_direction=signal.next_direction,
            signal_state=signal.state.value,
            remaining_seconds=signal.remaining_seconds,
            green_seconds=signal.green_seconds,
            model_ready=self.detector.available,
            signal_reason=signal.reason,
            processed_at=datetime.now(timezone.utc).isoformat(),
        )

    def process_frame(self, frame: Any, now: float | None = None) -> PipelineSnapshot:
        height, width = frame.shape[:2]
        detections = self.detector.track(frame)
        self.last_detections = detections
        lane_counts = {lane.value: 0 for lane in Lane}
        tracked_objects: list[tuple[int, str]] = []

        for detection in detections:
            lane = self.lane_mapper.lane_for_bbox(detection.bbox, width, height)
            if lane is None:
                continue
            lane_counts[lane.value] += 1
            if detection.track_id is not None:
                tracked_objects.append((detection.track_id, detection.label))

        self.tracker_counter.update(tracked_objects)
        vehicle_type_counts = self.tracker_counter.snapshot()
        densities = {
            lane: self.density.classify(count).value
            for lane, count in lane_counts.items()
        }
        signal = self.signal.update(lane_counts, now=now)
        self._last = PipelineSnapshot(
            total_tracked=self.tracker_counter.total,
            current_vehicle_count=sum(lane_counts.values()),
            vehicle_type_counts=vehicle_type_counts,
            lane_counts=lane_counts,
            lane_densities=densities,
            active_direction=signal.direction,
            next_direction=signal.next_direction,
            signal_state=signal.state.value,
            remaining_seconds=signal.remaining_seconds,
            green_seconds=signal.green_seconds,
            model_ready=True,
            signal_reason=signal.reason,
            processed_at=datetime.now(timezone.utc).isoformat(),
        )
        return self._last

    @property
    def snapshot(self) -> PipelineSnapshot:
        return self._last

    @property
    def is_all_red(self) -> bool:
        return self._last.signal_state == SignalState.ALL_RED.value
