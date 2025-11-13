"""
Custom exception handlers and middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from loguru import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors
    Provides better error messages for API consumers
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_type = error["type"]
        
        errors.append({
            "field": field,
            "message": message,
            "type": error_type
        })
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    General exception handler for unhandled errors
    """
    # Convert exception to string first to avoid loguru format string issues with curly braces
    exc_str = str(exc).replace('{', '{{').replace('}', '}}')
    logger.error(f"Unhandled exception on {request.url.path}: {exc_str}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if not isinstance(exc, Exception) else "An unexpected error occurred"
        }
    )


async def http_exception_handler(request: Request, exc):
    """
    Custom HTTP exception handler
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )
