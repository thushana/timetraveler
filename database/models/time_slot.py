from sqlalchemy import Column, Integer, String
from database.models.base import Base


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True)
    slot = Column(String(50), unique=True, nullable=False)
