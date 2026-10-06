from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..database.session import Base


class TrafficRecord(Base):
    __tablename__ = "traffic_records"
    __table_args__ = (
        Index("ix_traffic_records_recorded_at", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    total_vehicles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    north_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    east_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    south_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    west_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_direction: Mapped[str] = mapped_column(String(16), nullable=False)
    signal_state: Mapped[str] = mapped_column(String(16), nullable=False)
    remaining_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    green_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    vehicle_type_counts: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    average_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
