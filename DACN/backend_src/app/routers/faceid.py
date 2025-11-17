from fastapi import APIRouter, Request, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.faceid import (
    FaceAddResponse, FaceRecognitionResponse, FaceDeleteRequest
)
from app.validators import validate_face_image
from app.config import settings
from jose import jwt, JWTError
from loguru import logger
import numpy as np
import cv2
import base64
import os
import face_recognition
from PIL import Image
import io

router = APIRouter(tags=["faceid"])
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm

def extract_face_embedding(image_bytes):
    """
    Extract face embedding using face_recognition (dlib)
    Returns 128-dimensional face encoding
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)
        
        # Extract face encodings using face_recognition
        face_encodings = face_recognition.face_encodings(img_array, model='large')
        
        if len(face_encodings) == 0:
            return None, "No face detected in image"
        
        if len(face_encodings) > 1:
            logger.warning(f"Multiple faces detected ({len(face_encodings)}), using first one")
        
        return face_encodings[0], None
    except Exception as e:
        logger.error(f"Error extracting face embedding: {e}")
        return None, str(e)

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")

@router.post(
    "/add_face",
    response_model=FaceAddResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new face to the system"
)
async def add_face(
    image: UploadFile = File(..., description="Face image file"),
    name: str = Form(..., min_length=2, max_length=100, description="Person name")
):
    """
    Add a new face to the face recognition system
    
    - **image**: Face image file (JPG, JPEG, or PNG)
    - **name**: Person's name (2-100 characters)
    
    Returns face embedding data
    """
    # Validate image file
    try:
        validate_face_image(image)
    except HTTPException as e:
        logger.warning(f"Invalid face image: {e.detail}")
        return FaceAddResponse(
            success=False,
            message=e.detail
        )
    
    # Validate name
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty"
        )
    
    try:
        # Đọc file ảnh
        contents = await image.read()
        
        # Extract face embedding using face_recognition
        embedding, error_msg = extract_face_embedding(contents)
        
        if embedding is None:
            logger.warning(f"Failed to extract embedding for {name}: {error_msg}")
            return FaceAddResponse(
                success=False,
                message=error_msg or "Cannot detect face in image"
            )
        
        # Chuyển embedding thành base64 để trả về
        embedding_bytes = embedding.astype('float32').tobytes()
        embedding_b64 = base64.b64encode(embedding_bytes).decode('utf-8')
        
        logger.info(f"Successfully created embedding for {name}, size: {len(embedding)}")
        
        return JSONResponse({
            "success": True,
            "embedding_b64": embedding_b64,
            "name": name,
            "embedding_size": len(embedding)
        })
        
    except Exception as e:
        print(f"[ERROR] Lỗi khi xử lý ảnh: {e}")
        return JSONResponse({"success": False, "reason": str(e)}, status_code=500)

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
