from datetime import datetime

from pydantic import BaseModel, Field


class AnalyticsPoint(BaseModel):
    recorded_at: datetime
    total_vehicles: int = Field(ge=0)
    north: int = Field(ge=0)
    east: int = Field(ge=0)
    south: int = Field(ge=0)
    west: int = Field(ge=0)
    active_direction: str
    signal_state: str


class AnalyticsSummary(BaseModel):
    data_points: int = Field(ge=0)
    average_vehicles: float = Field(ge=0)
    peak_vehicles: int = Field(ge=0)
    minimum_vehicles: int = Field(ge=0)
    current_vehicles: int = Field(ge=0)
    busiest_lane: str
    lane_averages: dict[str, float]
    signal_state_counts: dict[str, int]


class PredictionPoint(BaseModel):
    horizon_minutes: int = Field(ge=1)
    predicted_total_vehicles: float = Field(ge=0)
    confidence: str
    method: str


class AnalyticsPrediction(BaseModel):
    data_points: int = Field(ge=0)
    predictions: list[PredictionPoint]
