from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers import employees, attendance, auth, faceid
from app.config import settings, ensure_upload_folder, ensure_log_folder
from app.middleware import (
    validation_exception_handler,
    general_exception_handler,
    http_exception_handler
)
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
import sys

# Setup logging
ensure_log_folder()
logger.remove()  # Remove default handler
logger.add(sys.stderr, level=settings.log_level)
logger.add(settings.log_file, rotation="500 MB", retention="10 days", level=settings.log_level)

app = FastAPI(
    title="DACN Attendance API",
    version="1.0.0",
    description="Face Recognition Attendance System API"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload folder exists
ensure_upload_folder()

# Mount static files
upload_path = str(settings.upload_folder)
logger.info(f"Mounting photos directory: {upload_path}")
app.mount("/photos", StaticFiles(directory=upload_path), name="photos")

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])
app.state.limiter = limiter

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return JSONResponse(
        status_code=429, 
        content={
            "detail": "Too many requests, please try again later.",
            "retry_after": 60
        }
    )

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Middleware logging request/response
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url} from {request.client.host}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as exc:
        logger.error(f"Request failed: {exc}")
        raise

app.include_router(employees.router, prefix="/employees", tags=["employees"])
app.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth.router, prefix="/auth", tags=["auth-legacy"])  # Legacy support for mobile app
app.include_router(faceid.router, prefix="/api/faceid")

@app.get("/")
def root():
    return {"message": "FaceID Attendance API"}

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    from app.cache import cache
    return {
        "status": "healthy",
        "database": "connected",
        "redis": cache.is_enabled(),
        "timestamp": datetime.now().isoformat(),
        "version": "1.3.0"
    }
