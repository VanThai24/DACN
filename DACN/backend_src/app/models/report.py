from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
    type = Column(String(50), nullable=False)
    file_path = Column(String(255))
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user = relationship("User")
