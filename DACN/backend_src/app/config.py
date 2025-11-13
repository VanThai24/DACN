"""
Configuration management for the application
Loads settings from environment variables with defaults
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database - MySQL connection
    database_url: str = "mysql+mysqlconnector://root:12345@127.0.0.1:3306/attendance_db"
    
    # JWT
    jwt_secret_key: str = "dev-secret-key-please-change"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # AI Model
    ai_model_path: str = "../AI/faceid_model_tf_best.h5"
    face_embedding_size: int = 128
    face_recognition_threshold: float = 0.6
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Flask AI Backend
    flask_ai_url: str = "http://localhost:5000"
    
    # File Upload
    max_upload_size: int = 10485760  # 10MB
    upload_folder: str = "../wwwroot/photos"
    allowed_extensions: str = "jpg,jpeg,png"  # Will be converted to list by validator
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@dacn.local"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Security
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    rate_limit_per_minute: int = 60
    api_keys: str = ""  # Comma-separated API keys
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # Environment
    environment: str = "development"
    
    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Convert comma-separated string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @field_validator("allowed_extensions", mode="after")
    @classmethod
    def parse_allowed_extensions(cls, v):
        """Convert comma-separated string to list"""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()


# Helper functions
def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment"""
    return settings.environment.lower() == "development"


def get_upload_path() -> Path:
    """Get absolute path for upload folder"""
    base_dir = Path(__file__).parent.parent.parent
    return base_dir / settings.upload_folder


def ensure_upload_folder():
    """Create upload folder if it doesn't exist"""
    upload_path = get_upload_path()
    upload_path.mkdir(parents=True, exist_ok=True)


def ensure_log_folder():
    """Create log folder if it doesn't exist"""
    log_path = Path(settings.log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)
