from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ai.detection.vehicle_detector import Detection
from ai.lane.lane_mapper import LaneMapper


EMERGENCY_LABELS = {
    "ambulance": "AMBULANCE",
    "firetruck": "FIRE_TRUCK",
    "fire_truck": "FIRE_TRUCK",
    "fire engine": "FIRE_TRUCK",
    "fire_engine": "FIRE_TRUCK",
    "police": "POLICE",
    "police car": "POLICE",
    "policecar": "POLICE",
    "police_car": "POLICE",
    "police vehicle": "POLICE",
    "police_vehicle": "POLICE",
    "emergency": "EMERGENCY_VEHICLE",
    "emergencyvehicle": "EMERGENCY_VEHICLE",
    "emergency_vehicle": "EMERGENCY_VEHICLE",
    "emergency vehicle": "EMERGENCY_VEHICLE",
    "rescue": "EMERGENCY_VEHICLE",
}


@dataclass(frozen=True)
class EmergencyEvent:
    detected: bool
    kind: str | None
    direction: str | None
    confidence: float
    track_id: int | None
    reason: str


def normalize_emergency_label(label: str) -> str | None:
    normalized = " ".join(label.strip().lower().replace("-", "_").split())
    return EMERGENCY_LABELS.get(normalized)


class EmergencyVehicleDetector:
    """Maps emergency-capable YOLO detections to an intersection direction."""

    def __init__(self, lane_mapper: LaneMapper | None = None) -> None:
        self.lane_mapper = lane_mapper or LaneMapper()

    def detect(
        self,
        detections: Iterable[Detection],
        width: int,
        height: int,
    ) -> EmergencyEvent:
        candidates: list[tuple[float, Detection, str]] = []
        for detection in detections:
            kind = normalize_emergency_label(detection.label)
            if kind is None:
                continue
            candidates.append((detection.confidence, detection, kind))

        if not candidates:
            return EmergencyEvent(
                detected=False,
                kind=None,
                direction=None,
                confidence=0.0,
                track_id=None,
                reason="no emergency-class detection",
            )

        confidence, detection, kind = max(
            candidates,
            key=lambda item: (item[0], item[1].track_id is not None),
        )
        lane = self.lane_mapper.lane_for_bbox(detection.bbox, width, height)
        direction = lane.value if lane is not None else None

        if direction is None:
            return EmergencyEvent(
                detected=True,
                kind=kind,
                direction=None,
                confidence=confidence,
                track_id=detection.track_id,
                reason="emergency detected outside mapped lane",
            )

        return EmergencyEvent(
            detected=True,
            kind=kind,
            direction=direction,
            confidence=confidence,
            track_id=detection.track_id,
            reason="emergency vehicle detected",
        )


def emergency_priority_allowed(event: EmergencyEvent, min_confidence: float = 0.50) -> bool:
    return (
        event.detected
        and event.direction is not None
        and event.confidence >= min_confidence
    )
