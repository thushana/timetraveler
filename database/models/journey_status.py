from sqlalchemy import Column, Integer, String
from database.models.base import Base

class JourneyStatus(Base):
    __tablename__ = 'journey_statuses'
    
    id = Column(Integer, primary_key=True)
    status = Column(String(50), unique=True, nullable=False)