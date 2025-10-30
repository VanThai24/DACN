

from fastapi import APIRouter, Request, Depends, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

router = APIRouter(tags=["faceid"])
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")

@router.post("/scan")
@limiter.limit("10/minute")
async def scan_faceid(request: Request, user=Depends(verify_jwt)):
    """
    Xác thực khuôn mặt từ embedding gửi lên, yêu cầu JWT token.
    - request: encodings (list)
    - response: success, message, user
    """
    data = await request.json()
    encodings = data.get("encodings", [])
    # TODO: Thực hiện xác thực khuôn mặt với dữ liệu encodings
    # Ví dụ: so sánh với database, trả về kết quả
    if encodings:
        # Giả sử luôn thành công
        return JSONResponse({"success": True, "message": "Đã nhận diện khuôn mặt!", "user": user})
    return JSONResponse({"success": False, "message": "Không có dữ liệu khuôn mặt!"}, status_code=400)
