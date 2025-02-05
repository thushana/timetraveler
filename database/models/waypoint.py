from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.models.base import Base

class Waypoint(Base):
    __tablename__ = 'waypoints'

    id = Column(Integer, primary_key=True, autoincrement=True)
    journey_id = Column(Integer, ForeignKey('journeys.id'), nullable=False)
    plus_code = Column(String, nullable=True)
    place_id = Column(String, nullable=True)
    formatted_address = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    journey = relationship('Journey', back_populates='waypoints')
