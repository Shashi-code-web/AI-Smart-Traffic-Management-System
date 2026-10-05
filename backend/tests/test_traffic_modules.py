from pathlib import Path

from ai.density.traffic_density import DensityConfig, TrafficDensityEstimator
from ai.lane.lane_mapper import Lane, LaneMapper
from ai.signals.adaptive_signal import AdaptiveSignalController, SignalConfig
from backend.app.services.demo_traffic import DemoTrafficSource
from backend.app.services.video_validator import resolve_video_path


def test_lane_mapper_default_regions():
    mapper = LaneMapper()
    assert mapper.lane_for_point(50, 50, 100, 100) is None
    assert mapper.lane_for_point(50, 10, 100, 100) == Lane.NORTH
    assert mapper.lane_for_point(50, 90, 100, 100) == Lane.SOUTH
    assert mapper.lane_for_point(90, 50, 100, 100) == Lane.EAST
    assert mapper.lane_for_point(10, 50, 100, 100) == Lane.WEST


def test_density_boundaries():
    estimator = TrafficDensityEstimator(DensityConfig(medium=10, high=25, critical=40))
    assert estimator.classify(9).value == "LOW"
    assert estimator.classify(10).value == "MEDIUM"
    assert estimator.classify(25).value == "HIGH"
    assert estimator.classify(40).value == "CRITICAL"


def test_signal_controller_prioritizes_highest_lane():
    controller = AdaptiveSignalController(SignalConfig(min_green=15, max_green=60))
    decision = controller.decide({"NORTH": 5, "EAST": 31, "SOUTH": 4, "WEST": 9})
    assert decision.direction == "EAST"
    assert 15 <= decision.green_seconds <= 60


def test_demo_source_changes_patterns_without_randomness():
    source = DemoTrafficSource(cycle_seconds=8)
    first = source.snapshot(now=0)
    second = source.snapshot(now=8)
    assert first.cycle_index != second.cycle_index
    assert first.counts != second.counts


def test_video_path_cannot_escape_video_directory():
    try:
        resolve_video_path("../../outside.mp4")
    except ValueError as exc:
        assert "data/videos" in str(exc)
    else:
        raise AssertionError("Path traversal was not rejected")
