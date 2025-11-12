from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Employee full name")
    department: Optional[str] = Field(None, max_length=100, description="Department name")
    role: Optional[str] = Field(None, max_length=50, description="Employee role")
    is_locked: Optional[int] = Field(0, ge=0, le=1, description="Account lock status")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    photo_path: Optional[str] = Field(None, max_length=500, description="Photo file path")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate employee name"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not re.match(r'^[\w\s\u00C0-\u1EF9]+$', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number"""
        if v is None:
            return v
        # Remove spaces and dashes
        phone = re.sub(r'[\s\-]', '', v)
        # Check if it's a valid phone number (10-15 digits)
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            raise ValueError('Invalid phone number format')
        return phone
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        """Validate role"""
        if v is None:
            return v
        allowed_roles = ['employee', 'admin', 'manager', 'staff']
        if v.lower() not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v.lower()


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=50)
    is_locked: Optional[int] = Field(None, ge=0, le=1)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    photo_path: Optional[str] = Field(None, max_length=500)


class Employee(EmployeeBase):
    """Schema for employee response"""
    id: int
    
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
    model_config = ConfigDict(from_attributes=True)
