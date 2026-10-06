from pydantic import BaseModel, Field


class LaneTraffic(BaseModel):
    direction: str
    vehicle_count: int = Field(ge=0)
    density: str
    signal: str
    remaining_seconds: int = Field(ge=0)


class TrafficSnapshot(BaseModel):
    total_vehicles: int = Field(ge=0)
    vehicle_type_counts: dict[str, int] = Field(default_factory=dict)
    active_direction: str
    next_direction: str
    signal_state: str
    remaining_seconds: int = Field(ge=0)
    green_seconds: int = Field(ge=0)
    signal_reason: str
    emergency_detected: bool = False
    emergency_type: str | None = None
    emergency_direction: str | None = None
    emergency_confidence: float = Field(default=0.0, ge=0, le=1)
    priority_active: bool = False
    lanes: list[LaneTraffic]
