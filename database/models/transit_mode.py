from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from database.models.base import Base


class TransitMode(Base):
    __tablename__ = "transit_modes"

    id = Column(Integer, primary_key=True)
    mode = Column(String(50), unique=True, nullable=False)

    @classmethod
    def get_id(cls, db: Session, mode: str) -> int:
        mode_key = mode.lower()
        if mode_key == "driving_routed":
            mode_key = "driving"

        mode_record: Optional[TransitMode] = db.query(cls).filter_by(mode=mode_key).first()
        if mode_record is not None:
            return int(mode_record.id)

        default_mode_record: Optional[TransitMode] = db.query(cls).filter_by(mode="driving").first()
        if default_mode_record is not None:
            return int(default_mode_record.id)

        raise ValueError("Default transit mode 'driving' not found in the database.")
