from backend_src.app.models.device import Device
from backend_src.app.database import Base
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    role = Column(String(50))
    face_embedding = Column(LargeBinary)
    is_locked = Column(Integer, nullable=False, default=0)
    photo_path = Column(String(255))
    attendance_records = relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    timestamp_in = Column(DateTime, nullable=False)
    timestamp_out = Column(DateTime)
    status = Column(String(50))
    photo_path = Column(String(255))
    employee = relationship("Employee", back_populates="attendance_records")
    device = relationship("Device", back_populates="attendance_records")
