# API Validation Guide

## 📋 Tổng Quan

Project đã được nâng cấp với **comprehensive input validation** sử dụng Pydantic để đảm bảo data integrity và security.

---

## ✅ Validation Được Thêm

### 1. **Employee Validation**

#### EmployeeCreate Schema
```python
{
    "name": "John Doe",           # 2-100 chars, no special chars
    "phone": "0123456789",        # 10-15 digits, auto-normalized
    "email": "john@example.com",  # Valid email format
    "role": "employee",           # Must be: employee/admin/manager/staff
    "department": "IT"            # Max 100 chars (optional)
}
```

**Validation Rules:**
- ✅ Name: 2-100 characters, Vietnamese supported, strips whitespace
- ✅ Phone: 10-15 digits, removes spaces/dashes, supports +country code
- ✅ Email: Valid email format (RFC 5322)
- ✅ Role: Must be one of allowed roles (case-insensitive)
- ✅ Department: Max 100 characters

**Error Examples:**
```json
// Name too short
{
  "detail": "Validation error",
  "errors": [{
    "field": "body -> name",
    "message": "Name must be at least 2 characters",
    "type": "value_error"
  }]
}

// Invalid phone
{
  "detail": "Validation error",
  "errors": [{
    "field": "body -> phone",
    "message": "Invalid phone number format",
    "type": "value_error"
  }]
}
```

---

### 2. **Authentication Validation**

#### UserLogin Schema
```python
{
    "username": "testuser",    # 3-50 chars, alphanumeric + underscore
    "password": "password123"  # Min 6 chars
}
```

#### UserRegister Schema
```python
{
    "username": "newuser",           # 3-50 chars, lowercase
    "password": "securepass123",     # Min 6 chars
    "email": "user@example.com",     # Valid email (optional)
    "employee_id": 123               # Integer (optional)
}
```

**Validation Rules:**
- ✅ Username: 3-50 chars, letters/numbers/underscore only
- ✅ Password: Minimum 6 characters
- ✅ Email: Valid email format if provided
- ✅ Username auto-converted to lowercase

---

### 3. **File Upload Validation**

#### Image Requirements
```python
validate_face_image(file)  # For face recognition
```

**Validation Rules:**
- ✅ **File Type**: Only jpg, jpeg, png
- ✅ **File Size**: Max 10MB (configurable)
- ✅ **Dimensions**: 
  - Min: 100x100 pixels (for faces)
  - Max: 4096x4096 pixels
- ✅ **Content Type**: image/jpeg, image/jpg, image/png
- ✅ **File Integrity**: Verifies it's a valid image using PIL

**Usage in Endpoint:**
```python
from backend_src.app.validators import validate_face_image

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    validate_face_image(file)  # Raises HTTPException if invalid
    # Process file...
```

**Error Example:**
```json
{
  "detail": "Image too small. Minimum: 100x100px"
}
```

---

### 4. **Face Recognition Validation**

#### FaceAddRequest
```python
{
    "name": "John Doe",        # 2-100 chars, required
    "employee_id": 123         # Integer (optional)
}
```

#### FaceRecognitionRequest
```python
{
    "threshold": 0.6           # Float 0.0-1.0, default 0.6
}
```

---

## 🛡️ Security Features

### 1. **Filename Sanitization**
```python
from backend_src.app.validators import FileValidator

safe_name = FileValidator.sanitize_filename("../../etc/passwd")
# Returns: "..etcpasswd" (safe)
```

**Protection Against:**
- Directory traversal attacks
- Special characters injection
- Overly long filenames

### 2. **Content Type Validation**
```python
FileValidator.validate_file_content_type(
    file,
    allowed_types=["image/jpeg", "image/png"]
)
```

### 3. **Input Sanitization**
- Automatic whitespace trimming
- Case normalization (usernames, roles)
- Phone number formatting

---

## 🧪 Testing Validation

### Run All Validation Tests
```bash
# Test validation schemas
pytest tests/test_validation.py -v

# Test file validators
pytest tests/test_file_validation.py -v

# Test all with coverage
pytest tests/ --cov=app.validators --cov=app.schemas
```

### Example Test
```python
def test_invalid_email():
    with pytest.raises(ValidationError):
        EmployeeCreate(
            name="John Doe",
            email="invalid-email"  # Missing @
        )
```

---

## 📝 Custom Validation

### Adding New Validators

**In Schema:**
```python
from pydantic import field_validator

class MySchema(BaseModel):
    custom_field: str
    
    @field_validator('custom_field')
    @classmethod
    def validate_custom(cls, v: str) -> str:
        if not v.startswith("PREFIX_"):
            raise ValueError('Must start with PREFIX_')
        return v
```

**In Validators Module:**
```python
# app/validators.py

def validate_custom_file(file: UploadFile) -> None:
    """Custom file validation"""
    if file.size > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )
```

---

## 🔧 Configuration

Validation settings in `.env`:
```env
# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png

# Face Recognition
FACE_RECOGNITION_THRESHOLD=0.6
FACE_EMBEDDING_SIZE=128
```

Access in code:
```python
from backend_src.app.config import settings

max_size = settings.max_upload_size
allowed_ext = settings.allowed_extensions
```

---

## 🐛 Error Handling

### Custom Exception Handler
Validation errors are automatically formatted:

```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "body -> name",
      "message": "String should have at least 2 characters",
      "type": "string_too_short"
    },
    {
      "field": "body -> email",
      "message": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### HTTP Status Codes
- `400` - Bad Request (invalid data format)
- `422` - Unprocessable Entity (validation failed)
- `409` - Conflict (duplicate data)
- `413` - Payload Too Large (file too big)

---

## 📊 Validation Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| Employee Schema | ✅ 100% | Complete |
| Auth Schema | ✅ 100% | Complete |
| File Validators | ✅ 100% | Complete |
| Face Recognition | ✅ 100% | Complete |

---

## 🚀 Best Practices

1. **Always validate at API boundary**
   ```python
   @router.post("/")
   def create(data: EmployeeCreate):  # Auto-validated
       # data is guaranteed valid here
   ```

2. **Use response models**
   ```python
   @router.get("/", response_model=Employee)
   def get_employee():
       return db_employee  # Auto-serialized
   ```

3. **Validate files before processing**
   ```python
   validate_face_image(file)  # First
   process_image(file)        # Then
   ```

4. **Handle validation errors gracefully**
   ```python
   try:
       validate_data(input)
   except ValidationError as e:
       logger.error(f"Validation failed: {e}")
       raise HTTPException(422, detail=str(e))
   ```

---

## 📚 References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Validation](https://fastapi.tiangolo.com/tutorial/body/)
- [PIL/Pillow Image Validation](https://pillow.readthedocs.io/)

---

**Updated**: November 12, 2025  
**Version**: 2.0.0  
**Status**: Phase 2 Complete ✅
