from fastapi import APIRouter, Depends, HTTPException, Body, status
from backend_src.app.database import SessionLocal
from backend_src.app.schemas.employee import Employee, EmployeeCreate, EmployeeUpdate
from backend_src.app.crud.employee import get_employee, create_employee, lock_employee, unlock_employee
from backend_src.app.config import settings
from backend_src.app.cache import cache, get_employee_key, get_face_embedding_key, EMPLOYEE_PREFIX
from loguru import logger
import base64
from sqlalchemy.orm import Session
import os
import requests

router = APIRouter(tags=["employees"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/{employee_id}/lock",
    response_model=Employee,
    status_code=status.HTTP_200_OK,
    summary="Lock employee account"
)
def lock_employee_api(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Lock an employee account to prevent access"""
    if employee_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee ID"
        )
    
    employee = lock_employee(db, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    logger.info(f"Locked employee ID: {employee_id}")
    return employee


@router.post(
    "/{employee_id}/unlock",
    response_model=Employee,
    status_code=status.HTTP_200_OK,
    summary="Unlock employee account"
)
def unlock_employee_api(
    employee_id: int,
    db: Session = Depends(get_db)
):
    """Unlock an employee account to restore access"""
    if employee_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee ID"
        )
    
    employee = unlock_employee(db, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    logger.info(f"Unlocked employee ID: {employee_id}")
    return employee

@router.post(
    "/",
    response_model=Employee,
    status_code=status.HTTP_201_CREATED,
    summary="Create new employee"
)
def create_employee_api(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new employee with validated data"""
    # Check if phone already exists
    if employee.phone:
        from backend_src.app.models.employee import Employee as EmployeeModel
        existing = db.query(EmployeeModel).filter_by(phone=employee.phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already exists"
            )
    
    # Tạo nhân viên
    db_employee = create_employee(db, employee)
    logger.info(f"Created employee: {db_employee.name} (ID: {db_employee.id})")
    
    ai_api_url = f"{settings.flask_ai_url}/add_face"
    photo_path = db_employee.photo_path
    
    abs_photo_path = None
    if photo_path:
        file_name = os.path.basename(photo_path)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        abs_photo_path = os.path.join(project_root, 'wwwroot', 'photos', file_name)

    if abs_photo_path and os.path.exists(abs_photo_path):
        try:
            with open(abs_photo_path, "rb") as img_file:
                files = {"image": img_file}
                data = {"name": db_employee.name}
                response = requests.post(ai_api_url, files=files, data=data)
            if response.ok:
                res_json = response.json()
                if res_json.get("success"):
                    embedding_b64 = res_json.get("embedding_b64")
                    if embedding_b64:
                        embedding_bytes = base64.b64decode(embedding_b64)
                        db_employee.face_embedding = embedding_bytes
                        db.commit()
                        db.refresh(db_employee)
                        logger.info(f"Saved face embedding for employee {db_employee.id}")
                    else:
                        logger.warning("No embedding received from AI backend")
                else:
                    logger.error(f"AI backend error: {res_json.get('reason')}")
            else:
                logger.error(f"Failed to connect to AI backend: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending image to AI backend: {e}")
    else:
        if abs_photo_path:
             logger.error(f"Image file not found: {abs_photo_path}")
        else:
             logger.info("Employee created without photo")

    # Làm mới dữ liệu từ DB và chuyển đổi sang dict
    db.refresh(db_employee)
    
    # Chuyển đổi thủ công sang dict để tránh lỗi validation
    employee_data = {
        "id": db_employee.id,
        "name": db_employee.name,
        "department": db_employee.department,
        "role": db_employee.role,
        "is_locked": db_employee.is_locked,
        "phone": db_employee.phone,
        "email": db_employee.email,
        "photo_path": db_employee.photo_path
    }
    
    # Invalidate employee list cache
    cache.delete_pattern(f"{EMPLOYEE_PREFIX}*")
    logger.debug(f"Invalidated employee cache after creation")
    
    return employee_data

@router.get(
    "/{employee_id}", 
    response_model=Employee,
    status_code=status.HTTP_200_OK,
    summary="Get employee by ID"
)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    """Get employee details with caching"""
    # Try cache first
    cache_key = get_employee_key(employee_id)
    cached_employee = cache.get(cache_key)
    if cached_employee:
        logger.debug(f"Cache hit for employee {employee_id}")
        return cached_employee
    
    # Get from database
    db_employee = get_employee(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Convert to dict
    employee_data = {
        "id": db_employee.id,
        "name": db_employee.name,
        "department": db_employee.department,
        "role": db_employee.role,
        "is_locked": db_employee.is_locked,
        "phone": db_employee.phone,
        "email": db_employee.email,
        "photo_path": db_employee.photo_path,
        "face_embedding": db_employee.face_embedding
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, employee_data, expire_seconds=300)
    logger.debug(f"Cached employee {employee_id}")
    
    return employee_data

# API cập nhật embedding khuôn mặt cho nhân viên
@router.post(
    "/{employee_id}/face_embedding",
    status_code=status.HTTP_200_OK,
    summary="Update face embedding"
)
def update_face_embedding(employee_id: int, embedding_b64: str = Body(...), db: Session = Depends(get_db)):
    """Update face embedding and cache it"""
    employee = get_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    try:
        embedding_bytes = base64.b64decode(embedding_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid embedding format (must be base64)")
    
    employee.face_embedding = embedding_bytes
    db.commit()
    db.refresh(employee)
    
    # Cache the face embedding (cache for 1 hour)
    embedding_cache_key = get_face_embedding_key(employee_id)
    cache.set(embedding_cache_key, embedding_bytes, expire_seconds=3600)
    
    # Invalidate employee cache
    employee_cache_key = get_employee_key(employee_id)
    cache.delete(employee_cache_key)
    
    logger.info(f"Updated and cached face embedding for employee {employee_id}")
    
    return {"success": True, "employee_id": employee_id}
