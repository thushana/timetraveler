from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Numeric, SmallInteger
from sqlalchemy.orm import relationship

from database.models.base import Base


class JourneyLeg(Base):
    __tablename__ = "journey_legs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journey_measurement_id = Column(Integer, ForeignKey("journey_measurements.id"), nullable=False)
    sequence_number = Column(SmallInteger, nullable=False)
    start_waypoint_id = Column(Integer, ForeignKey("journey_waypoints.id"), nullable=False)
    end_waypoint_id = Column(Integer, ForeignKey("journey_waypoints.id"), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    distance_meters = Column(Numeric(10, 2), nullable=False)
    speed_kph = Column(Numeric(5, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)

    measurement = relationship("JourneyMeasurement", back_populates="legs")
    start_waypoint = relationship("Waypoint", foreign_keys=[start_waypoint_id])
    end_waypoint = relationship("Waypoint", foreign_keys=[end_waypoint_id])
