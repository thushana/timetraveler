from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database.models.base import Base


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
