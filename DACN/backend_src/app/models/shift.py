from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    employee = relationship("Employee")
