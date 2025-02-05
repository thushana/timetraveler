from sqlalchemy import Column, Integer, String
from database.models.base import Base


class DayOfWeek(Base):
    __tablename__ = "days_of_week"

    id = Column(Integer, primary_key=True)
    day = Column(String(50), unique=True, nullable=False)
