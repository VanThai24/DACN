from fastapi import APIRouter, Request, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from backend_src.app.schemas.faceid import (
    FaceAddResponse, FaceRecognitionResponse, FaceDeleteRequest
)
from backend_src.app.validators import validate_face_image
from backend_src.app.config import settings
from jose import jwt, JWTError
from loguru import logger
import numpy as np
import cv2
import base64
import os
from tensorflow import keras

router = APIRouter(tags=["faceid"])
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm

# Load model AI để trích xuất embedding
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "AI", "faceid_model_tf.h5")
face_model = None

def load_face_model():
    global face_model
    if face_model is None:
        if os.path.exists(MODEL_PATH):
            face_model = keras.models.load_model(MODEL_PATH)
            # Build model bằng cách predict dummy data
            _ = face_model.predict(np.zeros((1, 128, 128, 3)), verbose=0)
            print(f"[INFO] Đã tải và build mô hình AI từ: {MODEL_PATH}")
        else:
            print(f"[WARNING] Không tìm thấy mô hình AI tại: {MODEL_PATH}")
    return face_model

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
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return FaceAddResponse(
                success=False,
                message="Cannot decode image file"
            )
        
        # Load mô hình AI
        model = load_face_model()
        if model is None:
            logger.error("AI model not available")
            return FaceAddResponse(
                success=False,
                message="AI model not ready"
            )
        
        # Tiền xử lý ảnh: resize về 128x128 (kích thước mô hình được huấn luyện) và chuẩn hóa
        img_resized = cv2.resize(img, (128, 128))
        img_normalized = img_resized.astype('float32') / 255.0
        img_batch = np.expand_dims(img_normalized, axis=0)
        
        # Lấy embedding từ layer Dense thứ 2 (128 chiều) thay vì softmax (6 chiều)
        # Predict model đầy đủ trước
        _ = model.predict(img_batch, verbose=0)
        
        # Tạo partial model bằng cách slice layers (không dùng model.input)
        from tensorflow.keras.models import Sequential
        embedding_layers = model.layers[:-1]  # Bỏ layer cuối (classification)
        partial_model = Sequential(embedding_layers)
        
        # Predict với partial model
        embedding = partial_model.predict(img_batch, verbose=0)
        embedding_flat = embedding.flatten()
        
        # Chuyển embedding thành base64 để trả về
        embedding_bytes = embedding_flat.astype('float32').tobytes()
        embedding_b64 = base64.b64encode(embedding_bytes).decode('utf-8')
        
        print(f"[INFO] Đã tạo embedding cho {name}, kích thước: {embedding_flat.shape}")
        
        return JSONResponse({
            "success": True,
            "embedding_b64": embedding_b64,
            "name": name,
            "embedding_size": len(embedding_flat)
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
