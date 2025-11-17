from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    api_key = Column(String(255), unique=True, nullable=False)
    last_seen = Column(DateTime)
    attendance_records = relationship("AttendanceRecord", back_populates="device")
