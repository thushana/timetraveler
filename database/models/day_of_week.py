from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from database.models.base import Base


class DayOfWeek(Base):
    __tablename__ = "days_of_week"

    id = Column(Integer, primary_key=True)
    day = Column(String(50), unique=True, nullable=False)

    @classmethod
    def get_day(cls, db: Session, day_id: int) -> str:
        """Retrieve the day name based on the given ID, or raise an error if not found."""
        day_record: Optional["DayOfWeek"] = db.query(cls).filter_by(id=day_id).first()
        if day_record is None:
            raise ValueError(f"Day with ID {day_id} not found in the database.")
        return str(day_record.day)  # Ensure explicit conversion to str
