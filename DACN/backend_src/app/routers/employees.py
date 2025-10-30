from fastapi import APIRouter, Depends, HTTPException, Body
from backend_src.app.database import SessionLocal
from backend_src.app.schemas.employee import Employee, EmployeeCreate
from backend_src.app.crud.employee import get_employee, create_employee, lock_employee, unlock_employee
import base64
from sqlalchemy.orm import Session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{employee_id}/lock", response_model=Employee)
def lock_employee_api(employee_id: int, db: Session = Depends(get_db)):
    employee = lock_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/{employee_id}/unlock", response_model=Employee)
def unlock_employee_api(employee_id: int, db: Session = Depends(get_db)):
    employee = unlock_employee(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.post("/", response_model=Employee)
def create_employee_api(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, employee)

@router.get("/{employee_id}", response_model=Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = get_employee(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

# API cập nhật embedding khuôn mặt cho nhân viên
@router.post("/{employee_id}/face_embedding")
def update_face_embedding(employee_id: int, embedding_b64: str = Body(...), db: Session = Depends(get_db)):
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
    return {"success": True, "employee_id": employee_id}
