import numpy as np

from ai.detection.vehicle_detector import Detection
from ai.emergency.emergency_vehicle import (
    EmergencyVehicleDetector,
    emergency_priority_allowed,
    normalize_emergency_label,
)
from ai.lane.lane_mapper import Lane
from ai.signals.adaptive_signal import AdaptiveSignalController, SignalConfig, SignalState


def test_phase7_normalizes_supported_emergency_labels():
    assert normalize_emergency_label("ambulance") == "AMBULANCE"
    assert normalize_emergency_label("Fire-Truck") == "FIRE_TRUCK"
    assert normalize_emergency_label("police car") == "POLICE"
    assert normalize_emergency_label("ordinary car") is None


def test_phase7_maps_emergency_detection_to_lane():
    detector = EmergencyVehicleDetector()
    event = detector.detect(
        [
            Detection(
                class_id=80,
                label="ambulance",
                confidence=0.91,
                bbox=(30, 0, 70, 30),
                track_id=42,
            )
        ],
        width=100,
        height=100,
    )

    assert event.detected is True
    assert event.kind == "AMBULANCE"
    assert event.direction == Lane.NORTH.value
    assert event.track_id == 42
    assert emergency_priority_allowed(event) is True


def test_phase7_low_confidence_emergency_does_not_preempt():
    detector = EmergencyVehicleDetector()
    event = detector.detect(
        [
            Detection(
                class_id=80,
                label="police",
                confidence=0.31,
                bbox=(70, 35, 90, 55),
                track_id=7,
            )
        ],
        width=100,
        height=100,
    )

    assert event.detected is True
    assert event.direction == Lane.EAST.value
    assert emergency_priority_allowed(event) is False


def test_phase7_emergency_priority_uses_safe_clearance_sequence():
    controller = AdaptiveSignalController(
        SignalConfig(min_green=5, max_green=30, yellow=3, all_red=1, emergency_green=20)
    )
    controller.reset(direction="NORTH", now=0)

    # Emergency approaches from EAST while NORTH is green.
    still_green = controller.update(
        {"NORTH": 1, "EAST": 1, "SOUTH": 1, "WEST": 1},
        now=4,
        priority_direction="EAST",
    )
    assert still_green.state == SignalState.GREEN
    assert still_green.direction == "NORTH"

    yellow = controller.update(
        {"NORTH": 1, "EAST": 1, "SOUTH": 1, "WEST": 1},
        now=5,
        priority_direction="EAST",
    )
    assert yellow.state == SignalState.YELLOW
    assert yellow.direction == "NORTH"
    assert yellow.next_direction == "EAST"

    all_red = controller.update(
        {"NORTH": 1, "EAST": 1, "SOUTH": 1, "WEST": 1},
        now=8,
        priority_direction="EAST",
    )
    assert all_red.state == SignalState.ALL_RED
    assert all_red.remaining_seconds == 1

    priority_green = controller.update(
        {"NORTH": 1, "EAST": 1, "SOUTH": 1, "WEST": 1},
        now=9,
        priority_direction="EAST",
    )
    assert priority_green.state == SignalState.GREEN
    assert priority_green.direction == "EAST"
    assert priority_green.priority_direction == "EAST"
    assert priority_green.green_seconds == 20

    sustained_yellow = controller.update(
        {"NORTH": 1, "EAST": 1, "SOUTH": 1, "WEST": 1},
        now=29,
        priority_direction="EAST",
    )
    assert sustained_yellow.state == SignalState.YELLOW
    assert sustained_yellow.direction == "EAST"
    assert sustained_yellow.next_direction == "EAST"

    sustained_all_red = controller.update(
        {"NORTH": 1, "EAST": 1, "SOUTH": 1, "WEST": 1},
        now=32,
        priority_direction="EAST",
    )
    assert sustained_all_red.state == SignalState.ALL_RED

    sustained_green = controller.update(
        {"NORTH": 1, "EAST": 1, "SOUTH": 1, "WEST": 1},
        now=33,
        priority_direction="EAST",
    )
    assert sustained_green.state == SignalState.GREEN
    assert sustained_green.direction == "EAST"
    assert sustained_green.green_seconds == 20


class _FakeDetector:
    available = True

    def track(self, _frame):
        return [
            Detection(
                class_id=80,
                label="ambulance",
                confidence=0.92,
                bbox=(30, 0, 70, 30),
                track_id=99,
            )
        ]


def test_phase7_pipeline_propagates_emergency_priority():
    from ai.pipeline.traffic_pipeline import TrafficPipeline

    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    pipeline = TrafficPipeline("models/yolo/test.pt")
    pipeline.detector = _FakeDetector()

    first = pipeline.process_frame(frame, now=0)
    assert first.emergency_detected is True
    assert first.emergency_type == "AMBULANCE"
    assert first.emergency_direction == Lane.NORTH.value
    assert first.priority_active is True
    assert first.signal_state == SignalState.GREEN
