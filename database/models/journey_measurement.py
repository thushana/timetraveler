import logging
from datetime import datetime, timezone
from typing import Any

import pytz
from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    func,
)
from sqlalchemy.orm import relationship

from database.models.base import Base

logger = logging.getLogger(__name__)  # Initialize logger


class JourneyMeasurement(Base):
    __tablename__ = "journey_measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journey_id = Column(Integer, ForeignKey("journeys.id"), nullable=False)
    transit_mode_id = Column(Integer, ForeignKey("transit_modes.id"), nullable=False)

    # UTC event time (calculated by the model)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    # Local event time (provided by the caller)
    local_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    # Auto-set database insertion time
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())

    # Day of week and time slot
    day_of_week_id = Column(Integer, ForeignKey("days_of_week.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)

    # Journey metrics
    duration_seconds = Column(Integer, nullable=False)
    distance_meters = Column(Numeric(10, 2), nullable=False)
    speed_kph = Column(Numeric(5, 2), nullable=False)

    # Raw API response
    raw_response = Column(JSON, nullable=True)

    # Relationships
    journey = relationship("Journey", back_populates="measurements")
    legs = relationship("JourneyLeg", back_populates="measurement", cascade="all, delete, delete-orphan")

    @staticmethod
    def ensure_utc(dt: datetime) -> datetime:
        """
        Ensure a datetime object is in UTC. Convert naive datetimes assuming they are UTC.
        """
        if dt.tzinfo is None:
            logger.debug(f"⏱️ ensure_utc TIME - ENSURE UTC (Naive -> UTC): Original: {dt.isoformat()} Assumed UTC: {dt.replace(tzinfo=timezone.utc).isoformat()}")
            return dt.replace(tzinfo=timezone.utc)
        utc_dt = dt.astimezone(timezone.utc)
        logger.debug(f"⏱️ ensure_utc TIME - ENSURE UTC (Aware -> UTC): Original: {dt.isoformat()} Converted UTC: {utc_dt.isoformat()}")
        return utc_dt


    def __init__(self, **kwargs: Any) -> None:
        """
        Custom initializer to ensure proper handling of timestamps.

        Args:
            **kwargs: Arbitrary keyword arguments, including:
                - local_timestamp (datetime): Local event timestamp.
                - journey (Journey): The associated journey with a `timezone` attribute.
        """
        local_timestamp: datetime = kwargs.get("local_timestamp")
        journey: Any = kwargs.get("journey")  # Replace `Any` with the correct Journey type if imported

        if not local_timestamp:
            raise ValueError("`local_timestamp` is required.")
        if not journey or not journey.timezone:
            raise ValueError("Journey with a valid `timezone` is required to calculate UTC `timestamp`.")

        # Ensure `local_timestamp` is timezone-aware
        if local_timestamp.tzinfo is None:
            local_timestamp = pytz.timezone(journey.timezone).localize(local_timestamp)
        kwargs["local_timestamp"] = local_timestamp  # Store local time as-is

        # Convert `local_timestamp` to UTC for `timestamp`
        kwargs["timestamp"] = local_timestamp.astimezone(pytz.utc)

        # Ensure `created_at` is always UTC
        kwargs["created_at"] = self.ensure_utc(kwargs.get("created_at", datetime.now(timezone.utc)))

        # Debug logging
        logger.debug(f"⏱️ init 2 TIME - TRIP LOCAL: {kwargs['local_timestamp'].isoformat()}")
        logger.debug(f"⏱️ init 2 TIME - UTC: {kwargs['timestamp'].isoformat()}")
        logger.debug(f"⏱️ init 2 TIME - CREATED_AT: {kwargs['created_at'].isoformat()}")

        super().__init__(**kwargs)
