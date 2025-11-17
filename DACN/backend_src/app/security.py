"""
Enhanced security utilities for the application
Includes JWT token management, password hashing, API key validation, and security middleware
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from loguru import logger
import secrets
import hashlib
import bleach
from html import escape
from cryptography.fernet import Fernet
import base64

from app.config import settings
from app.database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = settings.jwt_algorithm
SECRET_KEY = settings.jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt_refresh_token_expire_days

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ============= Password Management =============

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    # Bcrypt has a 72 byte limit, truncate if needed
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Bcrypt has a 72 byte limit, truncate if needed
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> bool:
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains digit
    - Contains special character
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return has_upper and has_lower and has_digit and has_special


# ============= Data Encryption =============

# Generate encryption key from SECRET_KEY (ensure it's 32 bytes for Fernet)
def _get_encryption_key() -> bytes:
    """Generate a valid Fernet key from SECRET_KEY"""
    # Hash the secret key to get 32 bytes
    key_hash = hashlib.sha256(SECRET_KEY.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_hash)


# Initialize Fernet cipher
_cipher_suite = Fernet(_get_encryption_key())


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data (phone, email, etc.)
    Returns base64 encoded encrypted string
    """
    if not data:
        return data
    try:
        encrypted = _cipher_suite.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise HTTPException(status_code=500, detail="Data encryption failed")


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data
    Returns original string
    """
    if not encrypted_data:
        return encrypted_data
    try:
        decrypted = _cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        # Only log warning for invalid format (not error, since it might be plain text)
        logger.warning(f"Decryption skipped (data may be plain text): {str(e)[:50]}")
        raise HTTPException(status_code=500, detail="Data decryption failed")


# ============= JWT Token Management =============

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Created access token for user: {data.get('sub')}")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Created refresh token for user: {data.get('sub')}")
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode JWT token
    Raises HTTPException if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token type. Expected {token_type}"
            )
        
        # Verify expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Log access for audit
    logger.info(f"Authenticated request from user: {user_id}")
    
    return {
        "user_id": user_id,
        "username": payload.get("username"),
        "role": payload.get("role")
    }


def require_role(allowed_roles: list):
    """
    Dependency to check user role
    Usage: current_user = Depends(require_role(["admin", "manager"]))
    """
    def role_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            logger.warning(f"Access denied for user {current_user.get('user_id')} with role {user_role}")
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


# ============= API Key Management =============

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify API key against hash"""
    return hash_api_key(api_key) == hashed_key


async def validate_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> bool:
    """
    Validate API key from header
    Used for AI backend and external services
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Check if API key is valid (you can store in database)
    # For now, check against environment variable
    valid_keys = getattr(settings, 'api_keys', '').split(',')
    
    if api_key not in valid_keys:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    logger.info("API key validated successfully")
    return True


# ============= Input Sanitization =============

def sanitize_html(text: str) -> str:
    """Remove HTML tags and escape special characters"""
    # Remove all HTML tags
    clean_text = bleach.clean(text, tags=[], strip=True)
    # Escape remaining special characters
    return escape(clean_text)


def sanitize_sql_input(text: str) -> str:
    """Sanitize input to prevent SQL injection"""
    # Remove dangerous SQL keywords and characters
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks
    """
    # Remove path separators and dangerous characters
    dangerous_chars = ['/', '\\', '..', '\0', ':', '*', '?', '"', '<', '>', '|']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized.strip()


# ============= Security Headers =============

def get_security_headers() -> Dict[str, str]:
    """Get recommended security headers"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }


# ============= Rate Limiting Helpers =============

def get_rate_limit_key(request: Request, suffix: str = "") -> str:
    """
    Generate rate limit key based on client IP and optional suffix
    """
    client_ip = request.client.host
    if suffix:
        return f"rate_limit:{client_ip}:{suffix}"
    return f"rate_limit:{client_ip}"


# ============= Audit Logging =============

class AuditLogger:
    """Audit logger for security-critical operations"""
    
    @staticmethod
    def log_login_attempt(username: str, success: bool, ip_address: str):
        """Log login attempt"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"LOGIN {status}: user={username}, ip={ip_address}")
        
        if not success:
            logger.warning(f"Failed login attempt for user {username} from {ip_address}")
    
    @staticmethod
    def log_logout(user_id: str, ip_address: str):
        """Log logout"""
        logger.info(f"LOGOUT: user_id={user_id}, ip={ip_address}")
    
    @staticmethod
    def log_user_creation(admin_id: str, new_user_id: str, ip_address: str):
        """Log user creation"""
        logger.info(f"USER_CREATED: admin={admin_id}, new_user={new_user_id}, ip={ip_address}")
    
    @staticmethod
    def log_user_deletion(admin_id: str, deleted_user_id: str, ip_address: str):
        """Log user deletion"""
        logger.warning(f"USER_DELETED: admin={admin_id}, deleted_user={deleted_user_id}, ip={ip_address}")
    
    @staticmethod
    def log_permission_change(admin_id: str, target_user_id: str, old_role: str, new_role: str, ip_address: str):
        """Log permission change"""
        logger.warning(f"PERMISSION_CHANGED: admin={admin_id}, user={target_user_id}, {old_role}->{new_role}, ip={ip_address}")
    
    @staticmethod
    def log_sensitive_data_access(user_id: str, data_type: str, record_id: str, ip_address: str):
        """Log access to sensitive data"""
        logger.info(f"DATA_ACCESS: user={user_id}, type={data_type}, record={record_id}, ip={ip_address}")
    
    @staticmethod
    def log_security_event(event_type: str, details: str, ip_address: str, user_id: Optional[str] = None):
        """Log generic security event"""
        user_info = f"user={user_id}, " if user_id else ""
        logger.warning(f"SECURITY_EVENT: {event_type}, {user_info}ip={ip_address}, details={details}")


# Create global audit logger instance
audit_logger = AuditLogger()


# ============= CSRF Protection =============

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, stored_token: str) -> bool:
    """Verify CSRF token"""
    return secrets.compare_digest(token, stored_token)
