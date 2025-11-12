"""
Authentication schemas with validation
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
import re


class UserLogin(BaseModel):
    """User login schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username or phone")
    password: str = Field(..., min_length=6, max_length=100, description="Password")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        # Allow alphanumeric, underscore, and numbers (for phone)
        if not re.match(r'^[a-zA-Z0-9_+]+$', v):
            raise ValueError('Username contains invalid characters')
        return v.strip()


class UserRegister(BaseModel):
    """User registration schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, max_length=100, description="Password")
    email: Optional[EmailStr] = Field(None, description="Email address")
    employee_id: Optional[int] = Field(None, description="Associated employee ID")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscore')
        return v.strip().lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 100:
            raise ValueError('Password is too long')
        # Check for at least one number or special character (optional but recommended)
        # if not re.search(r'[0-9]', v) and not re.search(r'[!@#$%^&*]', v):
        #     raise ValueError('Password should contain at least one number or special character')
        return v


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: Optional[str] = None
    employee_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class PasswordChange(BaseModel):
    """Password change schema"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str, info) -> str:
        """Validate new password"""
        if 'old_password' in info.data and v == info.data['old_password']:
            raise ValueError('New password must be different from old password')
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
