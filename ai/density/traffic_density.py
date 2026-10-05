from dataclasses import dataclass
from enum import StrEnum

class DensityLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass(frozen=True)
class DensityConfig:
    medium: int = 10
    high: int = 25
    critical: int = 40

class TrafficDensityEstimator:
    def __init__(self, config: DensityConfig | None = None):
        self.config = config or DensityConfig()

    def classify(self, vehicle_count: int) -> DensityLevel:
        if vehicle_count >= self.config.critical:
            return DensityLevel.CRITICAL
        if vehicle_count >= self.config.high:
            return DensityLevel.HIGH
        if vehicle_count >= self.config.medium:
            return DensityLevel.MEDIUM
        return DensityLevel.LOW
