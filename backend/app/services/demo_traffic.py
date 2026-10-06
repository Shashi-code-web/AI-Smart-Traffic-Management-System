from dataclasses import dataclass
import time

from ai.density.traffic_density import DensityConfig, TrafficDensityEstimator
from ai.signals.adaptive_signal import AdaptiveSignalController, SignalConfig


@dataclass(frozen=True)
class DemoTrafficSnapshot:
    counts: dict[str, int]
    densities: dict[str, str]
    active_direction: str
    next_direction: str
    signal_state: str
    remaining_seconds: int
    green_seconds: int
    cycle_index: int
    signal_reason: str


class DemoTrafficSource:
    """Deterministic offline traffic simulation using the same Phase 5 signal safety engine."""

    PATTERNS = (
        {"NORTH": 34, "EAST": 12, "SOUTH": 8, "WEST": 15},
        {"NORTH": 22, "EAST": 35, "SOUTH": 12, "WEST": 17},
        {"NORTH": 10, "EAST": 42, "SOUTH": 20, "WEST": 30},
        {"NORTH": 18, "EAST": 15, "SOUTH": 32, "WEST": 22},
    )

    def __init__(self, cycle_seconds: int = 8) -> None:
        self.cycle_seconds = max(1, cycle_seconds)
        self.estimator = TrafficDensityEstimator(DensityConfig())
        self.controller = AdaptiveSignalController(SignalConfig())

    def snapshot(self, now: float | None = None) -> DemoTrafficSnapshot:
        now = time.monotonic() if now is None else now
        cycle_index = int(now // self.cycle_seconds) % len(self.PATTERNS)
        counts = dict(self.PATTERNS[cycle_index])
        densities = {
            lane: self.estimator.classify(count).value
            for lane, count in counts.items()
        }
        signal = self.controller.update(counts, now=now)
        return DemoTrafficSnapshot(
            counts=counts,
            densities=densities,
            active_direction=signal.direction,
            next_direction=signal.next_direction,
            signal_state=signal.state.value,
            remaining_seconds=signal.remaining_seconds,
            green_seconds=signal.green_seconds,
            cycle_index=cycle_index,
            signal_reason=signal.reason,
        )
