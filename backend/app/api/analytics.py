from fastapi import APIRouter, Query

from ..schemas.analytics import (
    AnalyticsPoint,
    AnalyticsPrediction,
    AnalyticsSummary,
)
from ..services.traffic_analytics import traffic_analytics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _point(record) -> AnalyticsPoint:
    return AnalyticsPoint(
        recorded_at=record.recorded_at,
        total_vehicles=record.total_vehicles,
        north=record.north_count,
        east=record.east_count,
        south=record.south_count,
        west=record.west_count,
        active_direction=record.active_direction,
        signal_state=record.signal_state,
    )


@router.get("/history", response_model=list[AnalyticsPoint])
def history(limit: int = Query(default=100, ge=1, le=2000)):
    return [_point(record) for record in traffic_analytics.history(limit)]


@router.get("/summary", response_model=AnalyticsSummary)
def summary(limit: int = Query(default=100, ge=1, le=2000)):
    return AnalyticsSummary(**traffic_analytics.summary(limit))


@router.get("/predict", response_model=AnalyticsPrediction)
def predict(
    horizon: int = Query(default=5, ge=1, le=60),
    limit: int = Query(default=100, ge=1, le=2000),
):
    return AnalyticsPrediction(**traffic_analytics.predict(horizon, limit))
