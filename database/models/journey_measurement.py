from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from database.models.base import Base


class JourneyMeasurement(Base):
    __tablename__ = "journey_measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journey_id = Column(Integer, ForeignKey("journeys.id"), nullable=False)
    transit_mode_id = Column(Integer, ForeignKey("transit_modes.id"), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    local_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    day_of_week_id = Column(Integer, ForeignKey("days_of_week.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    distance_meters = Column(Numeric(10, 2), nullable=False)
    speed_kph = Column(Numeric(5, 2), nullable=False)
    raw_response = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

    journey = relationship("Journey", back_populates="measurements")
    legs = relationship(
        "JourneyLeg", back_populates="measurement", cascade="all, delete, delete-orphan"
    )
