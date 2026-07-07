from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class PlateRecord(Base):
    __tablename__ = "plate_records"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, index=True)
    image_path = Column(String)
    scanned_at = Column(DateTime, default=datetime.utcnow)
