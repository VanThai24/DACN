from fastapi import APIRouter, Depends, HTTPException, Body
from backend_src.app.database import SessionLocal
from backend_src.app.schemas.employee import Employee, EmployeeCreate
from backend_src.app.crud.employee import get_employee, create_employee, lock_employee, unlock_employee
import base64
from sqlalchemy.orm import Session
import os

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
    # Tạo nhân viên trước, sau đó lấy embedding nếu có ảnh
    db_employee = create_employee(db, employee)
    import requests, base64, os
    ai_api_url = "http://localhost:8000/api/faceid/add_face"  # Địa chỉ API faceid
    photo_path = db_employee.photo_path
    
    abs_photo_path = None
    if photo_path:
        # Lấy tên file cuối cùng để tránh lỗi lặp lại thư mục 'photos'
        file_name = os.path.basename(photo_path)
        # Xây dựng đường dẫn tuyệt đối từ gốc dự án (thư mục DACN)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        abs_photo_path = os.path.join(project_root, 'wwwroot', 'photos', file_name)

    print(f"[DEBUG] Đường dẫn tuyệt đối file ảnh: {abs_photo_path}")
    if abs_photo_path and os.path.exists(abs_photo_path):
        try:
            with open(abs_photo_path, "rb") as img_file:
                files = {"image": img_file}
                data = {"name": db_employee.name}
                response = requests.post(ai_api_url, files=files, data=data)
            print(f"[DEBUG] Response from AI backend: {response.status_code} {response.text}")
            if response.ok:
                res_json = response.json()
                if res_json.get("success"):
                    embedding_b64 = res_json.get("embedding_b64")
                    if embedding_b64:
                        embedding_bytes = base64.b64decode(embedding_b64)
                        db_employee.face_embedding = embedding_bytes
                        db.commit()
                        db.refresh(db_employee)
                        print("[INFO] Đã lưu embedding vào DB.")
                    else:
                        print("[WARNING] Không nhận được embedding từ AI backend.")
                else:
                    print(f"[ERROR] AI backend trả về lỗi: {res_json.get('reason')}")
            else:
                print(f"[ERROR] Không thể kết nối AI backend: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Lỗi khi gửi ảnh lên AI backend: {e}")
    else:
        if abs_photo_path:
             print(f"[ERROR] Không tồn tại file ảnh: {abs_photo_path}")
        else:
             print("[INFO] Nhân viên được tạo không có ảnh.")

    # Làm mới dữ liệu từ DB và chuyển đổi sang dict
    db.refresh(db_employee)
    
    # Chuyển đổi thủ công sang dict để tránh lỗi validation
    return {
        "id": db_employee.id,
        "name": db_employee.name,
        "department": db_employee.department,
        "role": db_employee.role,
        "is_locked": db_employee.is_locked,
        "phone": db_employee.phone,
        "email": db_employee.email,
        "photo_path": db_employee.photo_path
    }

@router.get("/{employee_id}", response_model=Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = get_employee(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Chuyển đối tượng ORM thành dict để trả về đúng response_model
    return {
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
