"""
Face recognition schemas with validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class FaceAddRequest(BaseModel):
    """Request to add a face to the system"""
    name: str = Field(..., min_length=2, max_length=100, description="Person name")
    employee_id: Optional[int] = Field(None, description="Associated employee ID")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class FaceAddResponse(BaseModel):
    """Response after adding a face"""
    success: bool
    message: str
    face_id: Optional[int] = None
    embedding_size: Optional[int] = None


class FaceRecognitionRequest(BaseModel):
    """Request to recognize a face"""
    threshold: Optional[float] = Field(0.6, ge=0.0, le=1.0, description="Recognition threshold")


class FaceRecognitionResponse(BaseModel):
    """Response from face recognition"""
    success: bool
    recognized: bool
    name: Optional[str] = None
    employee_id: Optional[int] = None
    confidence: Optional[float] = None
    message: Optional[str] = None


class FaceDeleteRequest(BaseModel):
    """Request to delete a face"""
    face_id: int = Field(..., gt=0, description="Face ID to delete")


class FaceUpdateRequest(BaseModel):
    """Request to update face information"""
    face_id: int = Field(..., gt=0, description="Face ID")
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    employee_id: Optional[int] = None


class FaceListResponse(BaseModel):
    """Response listing all faces"""
    success: bool
    faces: List[dict]
    total: int


class AttendanceCheckIn(BaseModel):
    """Check-in attendance request"""
    employee_id: Optional[int] = None
    location: Optional[str] = Field(None, max_length=200, description="Check-in location")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class AttendanceCheckOut(BaseModel):
    """Check-out attendance request"""
    attendance_id: int = Field(..., gt=0, description="Attendance record ID")
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceResponse(BaseModel):
    """Attendance record response"""
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    timestamp_in: datetime
    timestamp_out: Optional[datetime] = None
    status: str
    duration_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True


class AttendanceQuery(BaseModel):
    """Query parameters for attendance records"""
    employee_id: Optional[int] = Field(None, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)
    limit: int = Field(100, ge=1, le=1000, description="Maximum records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")
