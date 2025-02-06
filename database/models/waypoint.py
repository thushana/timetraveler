from __future__ import annotations  # Allows forward references for Journey

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text
from sqlalchemy.orm import Session, relationship

from database.models.base import Base
from database.models.journey import Journey


class Waypoint(Base):
    __tablename__ = "journey_waypoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journey_id = Column(Integer, ForeignKey("journeys.id"), nullable=False)
    sequence_number = Column(SmallInteger, nullable=False)
    place_id = Column(String, nullable=True)
    plus_code = Column(String, nullable=True)
    formatted_address = Column(Text, nullable=True)
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    journey = relationship("Journey", back_populates="waypoints")

    @classmethod
    def get_id(cls, db: Session, journey: Journey, address: str) -> int:
        waypoint = db.query(cls).filter_by(journey_id=journey.id, formatted_address=address).first()
        return int(waypoint.id) if waypoint else int(journey.waypoints[0].id)
