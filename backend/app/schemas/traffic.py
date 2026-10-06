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
    lanes: list[LaneTraffic]
