import logging
from datetime import datetime
from typing import cast

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from database.models.base import Base


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True)
    slot = Column(String(50), unique=True, nullable=False)

    @classmethod
    def get_id(cls, db: Session, dt: datetime) -> int:
        hour = dt.hour
        minute = (dt.minute // 15) * 15
        slot_key = f"{hour:02d}_{minute:02d}"

        if hour < 4:
            period = "overnight"
        elif hour < 8:
            period = "dawn"
        elif hour < 12:
            period = "morning"
        elif hour < 16:
            period = "afternoon"
        elif hour < 20:
            period = "evening"
        else:
            period = "night"

        slot_key = f"{slot_key}_{period}"
        slot = db.query(cls).filter_by(slot=slot_key).first()

        if not slot:
            logging.warning(f"Time slot key '{slot_key}' not found in the database.")
            raise ValueError(f"Time slot key '{slot_key}' not found.")

        return int(slot.id)
