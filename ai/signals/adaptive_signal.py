from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import math
import time


class SignalState(StrEnum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    ALL_RED = "ALL_RED"


@dataclass(frozen=True)
class SignalConfig:
    min_green: int = 15
    max_green: int = 60
    yellow: int = 3
    all_red: int = 1
    emergency_green: int = 20


@dataclass(frozen=True)
class SignalDecision:
    direction: str
    green_seconds: int
    reason: str


@dataclass(frozen=True)
class SignalSnapshot:
    state: SignalState
    direction: str
    next_direction: str
    remaining_seconds: int
    green_seconds: int
    yellow_seconds: int
    all_red_seconds: int
    priority_direction: str | None
    reason: str


class AdaptiveSignalController:
    """Four-way adaptive signal controller with explicit safety transition phases."""

    DIRECTIONS = ("NORTH", "EAST", "SOUTH", "WEST")

    def __init__(self, config: SignalConfig | None = None):
        self.config = config or SignalConfig()
        self._state = SignalState.GREEN
        self._direction = self.DIRECTIONS[0]
        self._next_direction = self.DIRECTIONS[0]
        self._phase_started_at: float | None = None
        self._green_seconds = self._clamp_green(self.config.min_green)
        self._priority_direction: str | None = None
        self._reason = "startup"

    def _validate_config(self) -> None:
        if self.config.min_green < 1:
            raise ValueError("min_green must be at least 1 second")
        if self.config.max_green < self.config.min_green:
            raise ValueError("max_green must be greater than or equal to min_green")
        if self.config.yellow < 1:
            raise ValueError("yellow must be at least 1 second")
        if self.config.all_red < 1:
            raise ValueError("all_red must be at least 1 second")
        if self.config.emergency_green < self.config.min_green:
            raise ValueError("emergency_green must be greater than or equal to min_green")

    def _clamp_green(self, seconds: int) -> int:
        return max(self.config.min_green, min(self.config.max_green, int(seconds)))

    def decide(self, densities: dict[str, int]) -> SignalDecision:
        """Return the best green direction and duration without mutating controller state."""
        self._validate_config()
        if not densities:
            return SignalDecision(
                self.DIRECTIONS[0],
                self.config.min_green,
                "default",
            )

        direction = max(
            self.DIRECTIONS,
            key=lambda d: (densities.get(d, 0), -self.DIRECTIONS.index(d)),
        )
        peak = max(0, max(densities.get(d, 0) for d in self.DIRECTIONS))
        span = self.config.max_green - self.config.min_green
        extra = min(span, peak * 2)
        duration = self._clamp_green(self.config.min_green + extra)
        return SignalDecision(
            direction=direction,
            green_seconds=duration,
            reason=f"highest lane demand={peak}",
        )

    def _select_next_direction(self, densities: dict[str, int]) -> SignalDecision:
        if self._priority_direction and self._priority_direction != self._direction:
            direction = self._priority_direction
            peak = max(0, densities.get(direction, 0))
            return SignalDecision(
                direction=direction,
                green_seconds=self._clamp_green(self.config.emergency_green),
                reason=f"emergency priority requested for {direction}",
            )

        decision = self.decide(densities)
        alternatives = {
            direction: max(0, densities.get(direction, 0))
            for direction in self.DIRECTIONS
            if direction != self._direction
        }
        if alternatives and max(alternatives.values()) > 0:
            direction = max(
                alternatives,
                key=lambda d: (alternatives[d], -self.DIRECTIONS.index(d)),
            )
            peak = alternatives[direction]
            span = self.config.max_green - self.config.min_green
            extra = min(span, peak * 2)
            return SignalDecision(
                direction=direction,
                green_seconds=self._clamp_green(self.config.min_green + extra),
                reason=f"highest alternative lane demand={peak}",
            )

        current_index = self.DIRECTIONS.index(self._direction)
        direction = self.DIRECTIONS[(current_index + 1) % len(self.DIRECTIONS)]
        return SignalDecision(
            direction=direction,
            green_seconds=decision.green_seconds,
            reason="round-robin fallback",
        )

    def request_priority(self, direction: str) -> None:
        self._validate_config()
        if direction not in self.DIRECTIONS:
            raise ValueError(f"Unknown priority direction: {direction}")
        self._priority_direction = direction

    def clear_priority(self) -> None:
        self._priority_direction = None

    def reset(self, direction: str = "NORTH", now: float | None = None) -> SignalSnapshot:
        self._validate_config()
        if direction not in self.DIRECTIONS:
            raise ValueError(f"Unknown direction: {direction}")
        self._direction = direction
        self._next_direction = direction
        self._state = SignalState.GREEN
        self._green_seconds = self.config.min_green
        self._priority_direction = None
        self._reason = "reset"
        self._phase_started_at = time.monotonic() if now is None else now
        return self.snapshot(now)

    def update(
        self,
        densities: dict[str, int],
        now: float | None = None,
        priority_direction: str | None = None,
    ) -> SignalSnapshot:
        """Advance the safety state machine using the latest lane demand."""
        self._validate_config()
        if priority_direction is not None:
            self.request_priority(priority_direction)
        else:
            self.clear_priority()
        current_time = time.monotonic() if now is None else now
        if self._phase_started_at is None:
            self._phase_started_at = current_time

        safety_limit = 8
        transitions = 0

        while transitions < safety_limit:
            duration = self._phase_duration()
            elapsed = max(0.0, current_time - self._phase_started_at)
            priority_cutover = (
                self._state is SignalState.GREEN
                and self._priority_direction is not None
                and self._priority_direction != self._direction
                and elapsed >= self.config.min_green
            )
            if elapsed < duration and not priority_cutover:
                break

            self._phase_started_at += duration
            self._advance_phase(densities)
            transitions += 1

        return self.snapshot(current_time)

    def _phase_duration(self) -> int:
        if self._state is SignalState.GREEN:
            return self._green_seconds
        if self._state is SignalState.YELLOW:
            return self.config.yellow
        return self.config.all_red

    def _advance_phase(self, densities: dict[str, int]) -> None:
        if self._state is SignalState.GREEN:
            decision = self._select_next_direction(densities)
            self._next_direction = decision.direction
            self._state = SignalState.YELLOW
            self._reason = "green expired; yellow transition"
            return

        if self._state is SignalState.YELLOW:
            self._state = SignalState.ALL_RED
            self._reason = "yellow expired; all-red safety clearance"
            return

        self._direction = self._next_direction
        if self._priority_direction == self._direction:
            self._green_seconds = self._clamp_green(self.config.emergency_green)
            self._reason = f"emergency priority active for {self._direction}"
        else:
            decision = self.decide({self._direction: densities.get(self._direction, 0)})
            self._green_seconds = decision.green_seconds
            self._reason = decision.reason
        self._state = SignalState.GREEN

    def snapshot(self, now: float | None = None) -> SignalSnapshot:
        current_time = time.monotonic() if now is None else now
        if self._phase_started_at is None:
            self._phase_started_at = current_time

        duration = self._phase_duration()
        elapsed = max(0.0, current_time - self._phase_started_at)
        remaining = max(0, int(math.ceil(duration - elapsed)))

        return SignalSnapshot(
            state=self._state,
            direction=self._direction,
            next_direction=self._next_direction,
            remaining_seconds=remaining,
            green_seconds=self._green_seconds,
            yellow_seconds=self.config.yellow,
            all_red_seconds=self.config.all_red,
            priority_direction=self._priority_direction,
            reason=self._reason,
        )
