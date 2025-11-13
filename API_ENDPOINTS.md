# 📡 API Endpoints - Backend Server

## 🌐 Base URL
```
http://192.168.110.29:8000
```
*Lưu ý: IP có thể thay đổi tùy mạng WiFi*

---

## 🔐 Authentication API

### 1. Login (Mobile App)
```http
POST /auth/login
POST /api/auth/login  (Cũng OK)
```

**Request Body:**
```json
{
  "username": "testuser",
  "password": "123456"
}
```

**Response Success (200):**
```json
{
  "id": 32,
  "username": "testuser",
  "full_name": "Nguyễn Văn Test",
  "role": "Employee",
  "department": "Phòng IT",
  "phone": "0123456789",
  "avatar": "/photos/testuser.jpg",
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Response Error (401):**
```json
{
  "detail": "Sai tài khoản hoặc mật khẩu"
}
```

**Rate Limit:** 5 requests/minute

---

## 👤 Employees API

### 1. Get Employee by ID
```http
GET /employees/{id}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": 32,
  "name": "Nguyễn Văn Test",
  "department": "Phòng IT",
  "role": "Nhân viên",
  "phone": "0123456789",
  "email": "testuser@company.com",
  "photo_path": "/photos/testuser.jpg",
  "is_locked": 0
}
```

### 2. Update Employee
```http
PUT /employees/{id}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "phone": "0987654321"
}
```

---

## 📅 Attendance API

### 1. Get Employee Attendance Records
```http
GET /attendance/employee/{employee_id}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
[
  {
    "id": 123,
    "employee_id": 32,
    "device_id": 1,
    "timestamp_in": "2025-11-12T08:00:00",
    "timestamp_out": "2025-11-12T17:30:00",
    "status": "out",
    "photo_path": "/photos/attendance_123.jpg"
  }
]
```

---

## 🤖 Face Recognition API

### 1. Add Face
```http
POST /api/faceid/add_face
```

**Headers:**
```
Content-Type: multipart/form-data
```

**Form Data:**
```
image: [file] (JPG/PNG)
name: "Nguyen Van A"
```

**Response Success (200):**
```json
{
  "success": true,
  "embedding_b64": "AAAAAACAPwAAgD8AAIA/...",
  "message": "Face added successfully",
  "name": "Nguyen Van A"
}
```

**Response Error (400):**
```json
{
  "detail": "No face detected in image"
}
```

---

## 🏥 Health Check

### 1. Root
```http
GET /
```

**Response:**
```json
{
  "message": "FaceID Attendance API"
}
```

### 2. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": false,
  "timestamp": "2025-11-12T19:20:00",
  "version": "1.3.0"
}
```

---

## 🔧 Mobile App Configuration

### File: `mobile_app/config.js`

```javascript
export const SERVER_IP = "192.168.110.29"; // Đổi IP này
export const API_URL = `http://${SERVER_IP}:8000`;
```

### Các endpoint Mobile App sử dụng:

| Screen | Method | Endpoint | Mục đích |
|--------|--------|----------|----------|
| Login | GET | `/` | Test connection |
| Login | POST | `/auth/login` | Đăng nhập |
| Home | GET | `/attendance/employee/{id}` | Lấy thống kê |
| Attendance | GET | `/attendance/employee/{id}` | Lịch sử điểm danh |
| Profile | PUT | `/employees/{id}` | Cập nhật SĐT |

---

## 🐛 Troubleshooting

### Lỗi 404 Not Found

**Nguyên nhân:** Route không tồn tại hoặc sai prefix

**Kiểm tra:**
1. Xem Backend logs: `INFO: "POST /auth/login HTTP/1.1" 404 Not Found`
2. Kiểm tra route trong `main.py`: `app.include_router(auth.router, prefix="/auth")`
3. Kiểm tra Mobile App gọi đúng endpoint

**Fix (đã áp dụng):**
```python
# main.py - Thêm cả 2 routes để support backward compatibility
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth.router, prefix="/auth", tags=["auth-legacy"])
```

### Lỗi 401 Unauthorized

**Nguyên nhân:** Token không hợp lệ hoặc hết hạn

**Giải pháp:**
1. Login lại để lấy token mới
2. Kiểm tra token có được gửi trong header không
3. Kiểm tra format: `Authorization: Bearer {token}`

### Lỗi 429 Too Many Requests

**Nguyên nhân:** Vượt quá rate limit (5 login/minute)

**Giải pháp:** Đợi 60 giây rồi thử lại

### Lỗi Connection Refused

**Nguyên nhân:** Backend API không chạy

**Giải pháp:**
```bash
cd D:\DACN
.venv\Scripts\python.exe -m uvicorn backend_src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📊 Swagger UI (API Documentation)

Truy cập: **http://192.168.110.29:8000/docs**

Hoặc ReDoc: **http://192.168.110.29:8000/redoc**

Tại đây bạn có thể:
- ✅ Xem tất cả endpoints
- ✅ Test API trực tiếp
- ✅ Xem request/response schema
- ✅ Thử các authentication flows

---

**Cập nhật:** 12/11/2025  
**Backend Version:** 1.3.0  
**API Base:** http://192.168.110.29:8000
