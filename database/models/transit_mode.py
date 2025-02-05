from sqlalchemy import Column, Integer, String

from database.models.base import Base


class TransitMode(Base):
    __tablename__ = "transit_modes"

    id = Column(Integer, primary_key=True)
    mode = Column(String(50), unique=True, nullable=False)
