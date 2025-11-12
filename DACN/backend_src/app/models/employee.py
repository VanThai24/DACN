from backend_src.app.models.device import Device
from backend_src.app.database import Base
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from backend_src.app.security import encrypt_data, decrypt_data

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)  # Index for name searches
    department = Column(String(100), index=True)  # Index for department filtering
    _phone = Column("phone", String(500), unique=True, index=True)  # Encrypted, larger size for encrypted data
    _email = Column("email", String(500), unique=True, index=True)  # Encrypted, larger size for encrypted data
    role = Column(String(50), index=True)  # Index for role filtering
    face_embedding = Column(LargeBinary)
    is_locked = Column(Integer, nullable=False, default=0, index=True)  # Index for locked status
    photo_path = Column(String(255))
    attendance_records = relationship("AttendanceRecord", back_populates="employee", cascade="all, delete-orphan")

    @hybrid_property
    def phone(self):
        """Automatically decrypt phone when accessed"""
        if self._phone:
            try:
                return decrypt_data(self._phone)
            except:
                return self._phone  # Return as-is if decryption fails (for migration compatibility)
        return self._phone

    @phone.setter
    def phone(self, value):
        """Automatically encrypt phone when set"""
        if value:
            self._phone = encrypt_data(value)
        else:
            self._phone = value

    @hybrid_property
    def email(self):
        """Automatically decrypt email when accessed"""
        if self._email:
            try:
                return decrypt_data(self._email)
            except:
                return self._email  # Return as-is if decryption fails (for migration compatibility)
        return self._email

    @email.setter
    def email(self, value):
        """Automatically encrypt email when set"""
        if value:
            self._email = encrypt_data(value)
        else:
            self._email = value

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    timestamp_in = Column(DateTime, nullable=False, index=True)  # Index for date queries
    timestamp_out = Column(DateTime, index=True)  # Index for date range queries
    status = Column(String(50), index=True)  # Index for status filtering
    photo_path = Column(String(255))
    employee = relationship("Employee", back_populates="attendance_records")
    device = relationship("Device", back_populates="attendance_records")
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_employee_date', 'employee_id', 'timestamp_in'),
        Index('idx_device_date', 'device_id', 'timestamp_in'),
    )
