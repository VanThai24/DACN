from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    name: str
    department: Optional[str] = None
    role: Optional[str] = None
    is_locked: Optional[int] = 0

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    is_locked: int
    class Config:
        orm_mode = True

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
