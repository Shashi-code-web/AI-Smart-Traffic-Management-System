from dataclasses import dataclass
from enum import StrEnum

class SignalState(StrEnum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

@dataclass(frozen=True)
class SignalConfig:
    min_green: int = 15
    max_green: int = 60
    yellow: int = 3
    all_red: int = 1

@dataclass
class SignalDecision:
    direction: str
    green_seconds: int
    reason: str

class AdaptiveSignalController:
    """Safe four-way signal scheduler: one direction is green at a time."""

    DIRECTIONS = ("NORTH", "EAST", "SOUTH", "WEST")

    def __init__(self, config: SignalConfig | None = None):
        self.config = config or SignalConfig()

    def decide(self, densities: dict[str, int]) -> SignalDecision:
        if not densities:
            return SignalDecision("NORTH", self.config.min_green, "default")
        direction = max(
            self.DIRECTIONS,
            key=lambda d: densities.get(d, 0),
        )
        peak = max(densities.values())
        span = self.config.max_green - self.config.min_green
        extra = min(span, max(0, peak) * 2)
        duration = min(self.config.max_green, self.config.min_green + extra)
        return SignalDecision(
            direction=direction,
            green_seconds=duration,
            reason=f"highest lane demand={peak}",
        )
