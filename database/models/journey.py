from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database.models.base import Base

class Journey(Base):
    __tablename__ = 'journeys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_name = Column(String, nullable=False)
    route_description = Column(String, nullable=True)
    original_url = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)

    waypoints = relationship('Waypoint', back_populates='journey', cascade="all, delete, delete-orphan")
