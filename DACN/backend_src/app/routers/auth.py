
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger

from ..database import get_db
from ..models import user as user_model
from ..models.employee import Employee as EmployeeModel
from ..security import (
    verify_password, 
    hash_password,
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_current_user,
    audit_logger,
    validate_password_strength,
    sanitize_html
)
from ..config import settings

# ============= Schemas =============

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    employee_id: Optional[int] = None  # 🔥 ADDED for mobile app
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.jwt_access_token_expire_minutes * 60  # seconds

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = settings.jwt_access_token_expire_minutes * 60

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "employee"

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ============= Router Setup =============

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post(
    "/login", 
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT tokens with strict rate limiting (5 attempts/minute)"
)
@limiter.limit("5/minute")  # Strict rate limit for login
def login(request_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Đăng nhập hệ thống, trả về thông tin người dùng và JWT tokens
    - Rate limit: 5 lần/phút để chống brute force
    - Audit logging cho mọi login attempt
    """
    client_ip = request.client.host
    
    # Sanitize username but NOT password
    # Password will be hashed, should not be HTML encoded
    username = sanitize_html(request_data.username.strip())
    password = request_data.password  # Keep password as-is for bcrypt
    
    try:
        # Find user
        user = db.query(user_model.User).filter(user_model.User.username == username).first()
        # Check credentials
        if not user or not verify_password(password, user.password_hash):
            # Log failed attempt
            audit_logger.log_login_attempt(username, False, client_ip)
            logger.warning(f"Failed login attempt for user '{username}' from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Sai tài khoản hoặc mật khẩu"
            )
        
        # Kiểm tra role - CHỈ employee/user mới được đăng nhập vào mobile app
        # Admin và Manager chỉ dùng web
        user_role = user.role.lower() if user.role else "employee"
        if user_role in ['admin', 'manager']:
            audit_logger.log_login_attempt(username, False, client_ip)
            logger.warning(f"Mobile login blocked for {user.role} '{username}' from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản Admin/Manager chỉ được đăng nhập trên Web. Vui lòng sử dụng tài khoản nhân viên để truy cập ứng dụng di động."
            )
        
        # Create tokens
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        # Log successful login
        audit_logger.log_login_attempt(username, True, client_ip)
        logger.info(f"Successful login for user '{username}' (ID: {user.id}) from {client_ip}")
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
            photo_path = employee.photo_path.strip()
            if photo_path:
                # Nếu photo_path đã có dấu / ở đầu thì giữ nguyên, nếu chỉ là tên file thì thêm /photos/
                if photo_path.startswith("/"):
                    avatar = photo_path
                else:
                    avatar = f"/photos/{photo_path}"
        
        logger.info(f"Login success - User: {user.username}, Employee ID: {user.employee_id}, Avatar: {avatar}")
        return LoginResponse(
            id=user.id,
            username=user.username,
            full_name=full_name,
            role=user.role,
            employee_id=user.employee_id,  # 🔥 ADDED for mobile app
            department=department,
            phone=phone,
            avatar=avatar,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"Login error: {ex}")
        audit_logger.log_security_event("LOGIN_ERROR", str(ex), client_ip, username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Đã xảy ra lỗi trong quá trình đăng nhập"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
@limiter.limit("10/minute")
def refresh_token_endpoint(
    token_request: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Làm mới access token bằng refresh token"""
    client_ip = request.client.host
    
    try:
        # Verify refresh token
        payload = verify_token(token_request.refresh_token, token_type="refresh")
        
        # Create new access token
        new_token_data = {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
        new_access_token = create_access_token(new_token_data)
        
        logger.info(f"Token refreshed for user {payload.get('username')} from {client_ip}")
        
        return TokenResponse(access_token=new_access_token)
        
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"Token refresh error: {ex}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create new user account with password strength validation (Rate limited: 3/hour)"
)
@limiter.limit("3/hour")  # Very strict rate limit for registration
def register(
    register_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Đăng ký tài khoản mới"""
    client_ip = request.client.host
    
    # Sanitize input
    username = sanitize_html(register_data.username.strip())
    full_name = sanitize_html(register_data.full_name.strip())
    password = sanitize_html(register_data.password)
    
    try:
        # Check if user already exists
        existing_user = db.query(user_model.User).filter(
            user_model.User.username == username
        ).first()
        if existing_user:
            logger.warning(f"Registration attempt with existing username '{username}' from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tên đăng nhập đã tồn tại"
            )
        # Validate password strength
        if not validate_password_strength(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt"
            )
        # Create new user
        hashed_password = hash_password(password)
        new_user = user_model.User(
            username=username,
            password_hash=hashed_password,
            role=register_data.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Log successful registration
        audit_logger.log_user_creation("system", str(new_user.id), client_ip)
        logger.info(f"New user registered: {username} (ID: {new_user.id}) from {client_ip}")
        return {
            "success": True,
            "message": "Đăng ký thành công",
            "user_id": new_user.id,
            "username": new_user.username
        }
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"Registration error: {ex}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi trong quá trình đăng ký"
        )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change user password with validation"
)
@limiter.limit("5/hour")
def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Sanitize input
        old_password = sanitize_html(password_data.old_password)
        new_password = sanitize_html(password_data.new_password)
        client_ip = request.client.host
        user_id = current_user.get("user_id")
        # Get user
        user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            logger.warning(f"Failed password change attempt for user {user_id} from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mật khẩu cũ không chính xác"
            )
        # Validate new password strength
        if not validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt"
            )
        # Check new password is different
        if old_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu mới phải khác mật khẩu cũ"
            )
        # Update password
        user.password_hash = hash_password(new_password)
        db.commit()
        # Log password change
        audit_logger.log_security_event("PASSWORD_CHANGED", f"User {user_id}", client_ip, str(user_id))
        logger.info(f"Password changed for user {user_id} from {client_ip}")
        return {
            "success": True,
            "message": "Đổi mật khẩu thành công"
        }
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"Change password error: {ex}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi trong quá trình đổi mật khẩu"
        )
        
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"Change password error: {ex}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi trong quá trình đổi mật khẩu"
        )


@router.get(
    "/me",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user info",
    description="Get current authenticated user information"
)
def get_me(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin user hiện tại"""
    try:
        user_id = current_user.get("user_id")
        user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )
        
        # Get employee info
        employee = None
        department = None
        phone = None
        avatar = None
        
        if user.employee_id:
            employee = db.query(EmployeeModel).filter(EmployeeModel.id == user.employee_id).first()
            if employee:
                department = employee.department
                phone = employee.phone
                
                # Construct avatar URL
                if employee.photo_path:
                    photo_path = employee.photo_path.strip()
                    if photo_path:
                        if photo_path.startswith("/"):
                            avatar = photo_path
                        else:
                            avatar = f"/photos/{photo_path}"
        
        # Create dummy tokens (not used but required by response model)
        access_token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
        refresh_token = create_refresh_token({"sub": str(user.id), "username": user.username, "role": user.role})
        
        return LoginResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            employee_id=user.employee_id,
            department=department,
            phone=phone,
            avatar=avatar,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    except HTTPException:
        raise
    except Exception as ex:
        logger.error(f"Get me error: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi lấy thông tin người dùng"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout and log the event"
)
def logout(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Đăng xuất"""
    client_ip = request.client.host
    user_id = current_user.get("user_id")
    
    # Log logout
    audit_logger.log_logout(str(user_id), client_ip)
    logger.info(f"User {user_id} logged out from {client_ip}")
    
    return {
        "success": True,
        "message": "Đăng xuất thành công"
    }
