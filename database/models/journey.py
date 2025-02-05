from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from database.models.base import Base

class Journey(Base):
    __tablename__ = 'journeys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    timezone = Column(Text, nullable=True)
    status_id = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    maps_url = Column(Text, nullable=True)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    waypoints = relationship('Waypoint', back_populates='journey', cascade="all, delete, delete-orphan")
    measurements = relationship('JourneyMeasurement', back_populates='journey', cascade="all, delete, delete-orphan")