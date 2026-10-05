from pydantic import BaseModel, Field

class LaneTraffic(BaseModel):
    direction: str
    vehicle_count: int = Field(ge=0)
    density: str
    signal: str
    remaining_seconds: int = Field(ge=0)

class TrafficSnapshot(BaseModel):
    total_vehicles: int = Field(ge=0)
    vehicle_type_counts: dict[str, int] = {}
    active_direction: str
    remaining_seconds: int = Field(ge=0)
    lanes: list[LaneTraffic]
