from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ai.counting.vehicle_counter import VehicleCounter
from ai.density.traffic_density import DensityConfig, TrafficDensityEstimator
from ai.detection.vehicle_detector import Detection, VehicleDetector
from ai.lane.lane_mapper import Lane, LaneMapper
from ai.signals.adaptive_signal import AdaptiveSignalController, SignalConfig


@dataclass(frozen=True)
class PipelineSnapshot:
    total_tracked: int
    current_vehicle_count: int
    lane_counts: dict[str, int]
    lane_densities: dict[str, str]
    active_direction: str
    green_seconds: int
    model_ready: bool
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
        return PipelineSnapshot(
            total_tracked=0,
            current_vehicle_count=0,
            lane_counts=counts,
            lane_densities={lane: self.density.classify(0).value for lane in counts},
            active_direction=Lane.NORTH.value,
            green_seconds=self.signal.config.min_green,
            model_ready=self.detector.available,
            processed_at=datetime.now(timezone.utc).isoformat(),
        )

    def process_frame(self, frame: Any) -> PipelineSnapshot:
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
        decision = self.signal.decide(lane_counts)
        densities = {
            lane: self.density.classify(count).value
            for lane, count in lane_counts.items()
        }
        self._last = PipelineSnapshot(
            total_tracked=self.tracker_counter.total,
            current_vehicle_count=sum(lane_counts.values()),
            lane_counts=lane_counts,
            lane_densities=densities,
            active_direction=decision.direction,
            green_seconds=decision.green_seconds,
            model_ready=True,
            processed_at=datetime.now(timezone.utc).isoformat(),
        )
        return self._last

    @property
    def snapshot(self) -> PipelineSnapshot:
        return self._last
