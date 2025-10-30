
from fastapi import APIRouter, Depends, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import user as user_model
from ..models.employee import Employee as EmployeeModel
from ..schemas import employee as employee_schema
from pydantic import BaseModel
from backend_src.app.security import verify_password
from jose import jwt
from datetime import datetime, timedelta

class LoginRequest(BaseModel):
    username: str
    password: str

from typing import Optional

class LoginResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    access_token: str
    token_type: str = "bearer"

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

SECRET_KEY = "your_secret_key_here"  # Nên lưu vào biến môi trường thực tế
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(request_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Đăng nhập hệ thống, trả về thông tin người dùng và JWT token nếu thành công.
    - request: username, password
    - response: id, username, full_name, role, department, phone, access_token, token_type
    """
    try:
        user = db.query(user_model.User).filter(user_model.User.username == request_data.username).first()
        if not user or not verify_password(request_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
        access_token = create_access_token(data={"sub": user.username, "user_id": user.id, "role": user.role})
        # Nếu user chưa liên kết employee, thử tự động liên kết theo username = phone
        employee = user.employee
        # Tự động liên kết employee nếu chưa có
        if not employee and user.username:
            employee = db.query(EmployeeModel).filter(EmployeeModel.phone == user.username).first()
            if employee:
                user.employee_id = employee.id
                db.commit()
        # Nếu employee đã có nhưng thiếu photo_path, tự động gán nếu có file trùng số điện thoại
        if employee and (not employee.photo_path or employee.photo_path.strip() == ""):
            import os
            photos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'wwwroot', 'photos'))
            # Tìm file ảnh trùng số điện thoại
            for file in os.listdir(photos_dir):
                if user.username in file:
                    employee.photo_path = file
                    db.commit()
                    break
        full_name = employee.name if employee and getattr(employee, "name", None) else user.username
        department = employee.department if employee and getattr(employee, "department", None) else "(Chưa cập nhật)"
        phone = employee.phone if employee and getattr(employee, "phone", None) else user.username
        avatar = None
        if employee and getattr(employee, "photo_path", None):
            # Nếu photo_path đã có dấu / ở đầu thì giữ nguyên, nếu chỉ là tên file thì thêm /photos/
            if employee.photo_path.startswith("/"):
                avatar = employee.photo_path
            else:
                avatar = f"/photos/{employee.photo_path}"
        return LoginResponse(
            id=user.id,
            username=user.username,
            full_name=full_name,
            role=user.role,
            department=department,
            phone=phone,
            avatar=avatar,
            access_token=access_token,
            token_type="bearer"
        )
    except Exception as ex:
        import traceback
        print("[LOGIN ERROR]", ex)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {ex}")
