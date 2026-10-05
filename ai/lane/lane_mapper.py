from dataclasses import dataclass
from enum import StrEnum


class Lane(StrEnum):
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"


@dataclass(frozen=True)
class NormalizedZone:
    x1: float
    y1: float
    x2: float
    y2: float

    def contains(self, x: float, y: float) -> bool:
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2


DEFAULT_ZONES: dict[Lane, NormalizedZone] = {
    Lane.NORTH: NormalizedZone(0.30, 0.00, 0.70, 0.30),
    Lane.SOUTH: NormalizedZone(0.30, 0.70, 0.70, 1.00),
    Lane.EAST: NormalizedZone(0.70, 0.30, 1.00, 0.70),
    Lane.WEST: NormalizedZone(0.00, 0.30, 0.30, 0.70),
}


class LaneMapper:
    """Maps detection centers to configurable normalized lane regions."""

    def __init__(self, zones: dict[Lane, NormalizedZone] | None = None):
        self.zones = zones or DEFAULT_ZONES

    def lane_for_point(self, x: float, y: float, width: int, height: int) -> Lane | None:
        if width <= 0 or height <= 0:
            return None
        nx = max(0.0, min(1.0, x / width))
        ny = max(0.0, min(1.0, y / height))
        for lane, zone in self.zones.items():
            if zone.contains(nx, ny):
                return lane
        return None

    def lane_for_bbox(self, bbox: tuple[int, int, int, int], width: int, height: int) -> Lane | None:
        x1, y1, x2, y2 = bbox
        return self.lane_for_point((x1 + x2) / 2, (y1 + y2) / 2, width, height)
