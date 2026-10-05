import numpy as np

from ai.counting.vehicle_counter import VehicleCounter
from ai.density.traffic_density import DensityConfig, TrafficDensityEstimator
from ai.detection.vehicle_detector import Detection
from ai.lane.lane_mapper import Lane
from ai.pipeline.traffic_pipeline import TrafficPipeline
from ai.signals.adaptive_signal import AdaptiveSignalController, SignalConfig


class FakeDetector:
    available = True

    def __init__(self, frames):
        self.frames = iter(frames)

    def track(self, _frame):
        return next(self.frames)


def test_vehicle_counter_keeps_unique_track_ids_and_class_counts():
    counter = VehicleCounter()
    counter.update([(1, "car"), (2, "bus"), (1, "car"), (3, "car")])

    assert counter.total == 3
    assert counter.snapshot() == {"car": 2, "bus": 1}


def test_density_thresholds_are_stable():
    estimator = TrafficDensityEstimator(DensityConfig(medium=10, high=25, critical=40))

    assert estimator.classify(9).value == "LOW"
    assert estimator.classify(10).value == "MEDIUM"
    assert estimator.classify(25).value == "HIGH"
    assert estimator.classify(40).value == "CRITICAL"


def test_signal_decision_prefers_highest_demand_and_respects_bounds():
    controller = AdaptiveSignalController(
        SignalConfig(min_green=15, max_green=60, yellow=3, all_red=1)
    )
    decision = controller.decide(
        {"NORTH": 5, "EAST": 12, "SOUTH": 30, "WEST": 4}
    )

    assert decision.direction == "SOUTH"
    assert 15 <= decision.green_seconds <= 60


def test_pipeline_counts_lanes_current_vehicles_and_unique_types():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    detections = [
        [
            Detection(2, "car", 0.90, (30, 0, 50, 20), 11),
            Detection(5, "bus", 0.93, (70, 35, 90, 55), 12),
            Detection(7, "truck", 0.88, (5, 35, 25, 55), 13),
        ],
        [
            Detection(2, "car", 0.91, (31, 1, 51, 21), 11),
            Detection(5, "bus", 0.92, (71, 36, 91, 56), 12),
            Detection(7, "truck", 0.87, (6, 36, 26, 56), 13),
        ],
    ]

    pipeline = TrafficPipeline("models/yolo/test.pt")
    pipeline.detector = FakeDetector(detections)

    first = pipeline.process_frame(frame)
    second = pipeline.process_frame(frame)

    assert first.current_vehicle_count == 3
    assert second.current_vehicle_count == 3
    assert second.total_tracked == 3
    assert second.vehicle_type_counts == {"car": 1, "bus": 1, "truck": 1}
    assert second.lane_counts[Lane.NORTH.value] == 1
    assert second.lane_counts[Lane.EAST.value] == 1
    assert second.lane_counts[Lane.WEST.value] == 1
    assert second.active_direction == Lane.NORTH.value or second.active_direction in {
        lane.value for lane in Lane
    }
