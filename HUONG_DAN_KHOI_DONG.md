# 🚀 HƯỚNG DẪN KHỞI ĐỘNG HỆ THỐNG

## ⚠️ LƯU Ý QUAN TRỌNG

**AdminWeb cần Backend API để xử lý Face Embedding!**

Khi Admin thêm nhân viên có upload ảnh khuôn mặt, AdminWeb sẽ gọi Backend API (port 8000) để:
1. Nhận diện khuôn mặt từ ảnh
2. Trích xuất face embedding
3. Lưu vào database

Nếu Backend API không chạy → Nhân viên vẫn được tạo nhưng **KHÔNG CÓ FACE ID** → Không thể điểm danh bằng khuôn mặt!

---

## 📋 Trình tự khởi động ĐÚNG

### Bước 1: Khởi động Backend API (QUAN TRỌNG!)

**Cách 1: Dùng script tự động (Khuyến nghị)**
```bash
# Mở terminal mới và chạy:
cd D:\DACN\DACN
start_backend.bat
```

**Cách 2: Chạy thủ công**
```bash
# Terminal 1: Backend API
cd D:\DACN\DACN\backend_src
D:\DACN\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Kiểm tra Backend đã chạy:**
- Mở browser: http://localhost:8000/docs
- Nếu thấy Swagger UI → Backend OK ✅
- Nếu không kết nối được → Kiểm tra lại lệnh

### Bước 2: Khởi động AdminWeb

```bash
# Terminal 2: AdminWeb
cd D:\DACN\DACN
dotnet run
# hoặc
dotnet watch run
```

**Truy cập:** http://localhost:5280

### Bước 3: Test Mobile App (Optional)

```bash
# Terminal 3: Mobile App
cd D:\DACN\DACN\mobile_app
npm start
```

---

## 🔍 Xử lý lỗi thường gặp

### ❌ "Không thể kết nối Backend API (port 8000)"

**Nguyên nhân:** Backend API chưa chạy

**Giải pháp:**
1. Mở terminal mới
2. Chạy `start_backend.bat`
3. Chờ đến khi thấy: `Uvicorn running on http://0.0.0.0:8000`
4. Thử thêm nhân viên lại trong AdminWeb

### ❌ "Không nhận diện được khuôn mặt"

**Nguyên nhân:** 
- Ảnh không rõ mặt
- Ảnh có nhiều người
- Góc chụp không phù hợp

**Giải pháp:**
- Upload ảnh chân dung, nhìn thẳng camera
- Ánh sáng tốt, không bị mờ
- Chỉ có 1 khuôn mặt trong ảnh

### ❌ "API returned error: 500"

**Nguyên nhân:** Backend API lỗi khi xử lý ảnh

**Giải pháp:**
1. Kiểm tra log terminal Backend API
2. Kiểm tra model AI đã tồn tại: `AI/faceid_model_tf_best.h5`
3. Restart Backend API

---

## 📊 Kiểm tra trạng thái hệ thống

### Backend API
```bash
# Test endpoint
curl http://localhost:8000/
# hoặc mở browser: http://localhost:8000/docs
```

### AdminWeb
```bash
# Kiểm tra đang chạy
curl http://localhost:5280
```

### MySQL Database
```bash
# Kiểm tra kết nối
D:\DACN\.venv\Scripts\python.exe D:\DACN\DACN\check_mysql_structure.py
```

---

## 🎯 Flow thêm nhân viên với Face ID

```
Admin upload ảnh trong AdminWeb
         ↓
AdminWeb gửi POST http://localhost:8000/api/faceid/add_face
         ↓
Backend API nhận diện khuôn mặt
         ↓
Trích xuất face embedding (128 dimensions)
         ↓
Trả về embedding dạng base64
         ↓
AdminWeb lưu vào database (employees.face_embedding)
         ↓
Nhân viên có Face ID → Có thể điểm danh bằng khuôn mặt ✅
```

---

## 🛠 Công cụ hỗ trợ

### 1. Start Backend API
```bash
D:\DACN\DACN\start_backend.bat
```

### 2. Xem danh sách users
```bash
D:\DACN\.venv\Scripts\python.exe D:\DACN\DACN\list_users.py
```

### 3. Thêm tài khoản test
```bash
D:\DACN\.venv\Scripts\python.exe D:\DACN\DACN\add_test_employee_mysql.py
```

### 4. Chuẩn hóa Role
```bash
D:\DACN\.venv\Scripts\python.exe D:\DACN\DACN\normalize_roles.py
```

---

## 📝 Tài khoản đăng nhập

### AdminWeb (http://localhost:5280)
```
Username: admin
Password: [Hỏi admin]
Role: Admin
```

### Mobile App
```
Username: testuser
Password: 123456
Role: Employee
```

---

## 🔧 Troubleshooting nâng cao

### Backend API không start được

**Lỗi: ModuleNotFoundError**
```bash
cd D:\DACN\DACN\backend_src
D:\DACN\.venv\Scripts\pip.exe install -r requirements.txt
```

**Lỗi: Port 8000 đã được sử dụng**
```bash
# Tìm process đang dùng port 8000
netstat -ano | findstr :8000
# Kill process
taskkill /PID <PID> /F
```

### AdminWeb lỗi MySQL connection

**Kiểm tra connection string:**
```bash
# File: appsettings.json
"DefaultConnection": "server=127.0.0.1;port=3306;database=attendance_db;uid=root;pwd=12345;"
```

**Restart MySQL:**
- Mở Services (services.msc)
- Tìm MySQL
- Restart

### Build AdminWeb bị lỗi

```bash
cd D:\DACN\DACN
dotnet clean
dotnet build
```

---

## ✅ Checklist khởi động

- [ ] MySQL đang chạy
- [ ] Backend API chạy trên port 8000
- [ ] AdminWeb chạy trên port 5280
- [ ] Database có dữ liệu test
- [ ] Đã test thêm nhân viên có ảnh
- [ ] Face embedding được lưu vào database

---

**Cập nhật:** 12/11/2025  
**Version:** 2.0  
**Support:** DACN Team
