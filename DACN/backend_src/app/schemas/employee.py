from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str
    department: Optional[str] = None
    role: Optional[str] = None
    is_locked: Optional[int] = 0
    phone: Optional[str] = None
    email: Optional[str] = None
    photo_path: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: Optional[int] = None
    
    class Config:
        from_attributes = True

class AttendanceRecordBase(BaseModel):
    employee_id: int
    timestamp_in: Optional[datetime] = None
    timestamp_out: Optional[datetime] = None
    status: Optional[str] = None
    photo_path: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecord(AttendanceRecordBase):
    id: int
    class Config:
        orm_mode = True
