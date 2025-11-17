"""
Tests for file upload validation
"""
import pytest
from fastapi import UploadFile, HTTPException
from app.validators import FileValidator, validate_face_image
from io import BytesIO
from PIL import Image


@pytest.fixture
def valid_image_file():
    """Create a valid test image"""
    img = Image.new('RGB', (200, 200), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return UploadFile(
        filename="test.jpg",
        file=img_bytes,
        content_type="image/jpeg"
    )


@pytest.fixture
def small_image_file():
    """Create a small image (too small)"""
    img = Image.new('RGB', (50, 50), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return UploadFile(
        filename="small.jpg",
        file=img_bytes,
        content_type="image/jpeg"
    )


@pytest.fixture
def large_image_file():
    """Create a large image"""
    img = Image.new('RGB', (6000, 6000), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return UploadFile(
        filename="large.jpg",
        file=img_bytes,
        content_type="image/jpeg"
    )


class TestFileValidator:
    """Test file validation utilities"""
    
    def test_valid_image(self, valid_image_file):
        """Test validation passes for valid image"""
        # Should not raise exception
        FileValidator.validate_image(valid_image_file)
    
    def test_image_too_small(self, small_image_file):
        """Test validation fails for small image"""
        with pytest.raises(HTTPException) as exc_info:
            FileValidator.validate_image(small_image_file, min_width=100, min_height=100)
        assert exc_info.value.status_code == 400
        assert "too small" in exc_info.value.detail.lower()
    
    def test_image_too_large(self, large_image_file):
        """Test validation fails for large image"""
        with pytest.raises(HTTPException) as exc_info:
            FileValidator.validate_image(large_image_file, max_width=5000, max_height=5000)
        assert exc_info.value.status_code == 400
        assert "too large" in exc_info.value.detail.lower()
    
    def test_invalid_file_extension(self):
        """Test validation fails for invalid extension"""
        invalid_file = UploadFile(
            filename="test.txt",
            file=BytesIO(b"not an image"),
            content_type="text/plain"
        )
        with pytest.raises(HTTPException) as exc_info:
            FileValidator.validate_image(invalid_file)
        assert exc_info.value.status_code == 400
        assert "invalid file type" in exc_info.value.detail.lower()
    
    def test_empty_file(self):
        """Test validation fails for empty file"""
        empty_file = UploadFile(
            filename="empty.jpg",
            file=BytesIO(b""),
            content_type="image/jpeg"
        )
        with pytest.raises(HTTPException) as exc_info:
            FileValidator.validate_image(empty_file)
        assert exc_info.value.status_code == 400
        assert "empty" in exc_info.value.detail.lower()
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        dangerous_filename = "../../../etc/passwd"
        safe = FileValidator.sanitize_filename(dangerous_filename)
        assert ".." not in safe
        assert "/" not in safe
        assert "\\" not in safe
    
    def test_sanitize_filename_special_chars(self):
        """Test special characters are removed"""
        filename = "test@#$%^&*().jpg"
        safe = FileValidator.sanitize_filename(filename)
        assert "@" not in safe
        assert "#" not in safe
        # Should keep extension
        assert safe.endswith(".jpg")
    
    def test_filename_length_limit(self):
        """Test filename length is limited"""
        long_filename = "a" * 200 + ".jpg"
        safe = FileValidator.sanitize_filename(long_filename)
        assert len(safe) <= 104  # 100 + ".jpg"
    
    def test_validate_content_type(self, valid_image_file):
        """Test content type validation"""
        allowed_types = ["image/jpeg", "image/png"]
        # Should not raise exception
        FileValidator.validate_file_content_type(valid_image_file, allowed_types)
    
    def test_invalid_content_type(self):
        """Test invalid content type rejection"""
        invalid_file = UploadFile(
            filename="test.jpg",
            file=BytesIO(b"data"),
            content_type="application/pdf"
        )
        with pytest.raises(HTTPException) as exc_info:
            FileValidator.validate_file_content_type(
                invalid_file,
                ["image/jpeg", "image/png"]
            )
        assert exc_info.value.status_code == 400


class TestFaceImageValidation:
    """Test face-specific image validation"""
    
    def test_valid_face_image(self, valid_image_file):
        """Test face image validation passes"""
        # Should not raise exception
        validate_face_image(valid_image_file)
    
    def test_face_image_too_small(self, small_image_file):
        """Test face image must meet minimum size"""
        with pytest.raises(HTTPException) as exc_info:
            validate_face_image(small_image_file)
        assert exc_info.value.status_code == 400
