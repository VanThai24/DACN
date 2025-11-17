"""
File upload validation utilities
"""
from fastapi import UploadFile, HTTPException
from typing import List
import os
from PIL import Image
import io
from app.config import settings


class FileValidator:
    """Validate uploaded files"""
    
    @staticmethod
    def validate_image(
        file: UploadFile,
        max_size: int = None,
        allowed_extensions: List[str] = None,
        min_width: int = 50,
        min_height: int = 50,
        max_width: int = 5000,
        max_height: int = 5000
    ) -> None:
        """
        Validate image file upload
        
        Args:
            file: Uploaded file
            max_size: Maximum file size in bytes
            allowed_extensions: List of allowed file extensions
            min_width: Minimum image width
            min_height: Minimum image height
            max_width: Maximum image width
            max_height: Maximum image height
            
        Raises:
            HTTPException: If validation fails
        """
        if max_size is None:
            max_size = settings.max_upload_size
        
        if allowed_extensions is None:
            allowed_extensions = settings.allowed_extensions
        
        # Check file exists
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        try:
            contents = file.file.read()
            file.file.seek(0)  # Reset file pointer
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
        
        # Check file size
        file_size = len(contents)
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size / (1024*1024):.1f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Validate image using PIL
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()  # Verify it's actually an image
            
            # Re-open for dimensions check (verify() closes the file)
            image = Image.open(io.BytesIO(contents))
            width, height = image.size
            
            # Check dimensions
            if width < min_width or height < min_height:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image too small. Minimum: {min_width}x{min_height}px"
                )
            
            if width > max_width or height > max_height:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image too large. Maximum: {max_width}x{max_height}px"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {str(e)}"
            )
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal attacks
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        import re
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Limit length
        name, ext = os.path.splitext(filename)
        if len(name) > 100:
            name = name[:100]
        
        return name + ext
    
    @staticmethod
    def validate_file_content_type(file: UploadFile, allowed_types: List[str]) -> None:
        """
        Validate file content type
        
        Args:
            file: Uploaded file
            allowed_types: List of allowed MIME types
            
        Raises:
            HTTPException: If content type is not allowed
        """
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type. Allowed: {', '.join(allowed_types)}"
            )


def validate_face_image(file: UploadFile) -> None:
    """
    Validate face image for face recognition
    Stricter validation for face detection
    """
    FileValidator.validate_image(
        file=file,
        max_size=settings.max_upload_size,
        allowed_extensions=settings.allowed_extensions,
        min_width=100,  # Minimum for face detection
        min_height=100,
        max_width=4096,
        max_height=4096
    )
    
    # Also validate content type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
    FileValidator.validate_file_content_type(file, allowed_types)
