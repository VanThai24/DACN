# 🚀 HƯỚNG DẪN CHẠY PROJECT HOÀN CHỈNH

## 📋 YÊU CẦU HỆ THỐNG

### Software
- Python 3.8+ (khuyến nghị 3.10)
- Node.js 16+ (cho mobile app)
- MySQL 8.0+
- Visual Studio Build Tools (cho Windows - build dlib)
- .NET 9.0 SDK (cho Admin Web)

### Hardware
- Webcam (cho desktop app face recognition)
- RAM: Tối thiểu 4GB, khuyến nghị 8GB+
- CPU: Hỗ trợ AVX (cho dlib optimization)

---

## 🔧 SETUP TỪNG BƯỚC

### 1️⃣ **Database Setup**

```bash
# Tạo database
mysql -u root -p
CREATE DATABASE attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE attendance_db;

# Import schema (nếu có file SQL)
source database_schema.sql;

# Hoặc chạy migrations
cd DACN/backend_src
alembic upgrade head
```

### 2️⃣ **Python Virtual Environment**

```powershell
# Tạo venv
cd D:\DACN
python -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Update pip
python -m pip install --upgrade pip
```

### 3️⃣ **Backend API (FastAPI)**

```powershell
# Install dependencies
cd DACN\backend_src
pip install -r requirements.txt

# Tạo file .env (copy từ .env.example)
cp .env.example .env

# Chỉnh sửa .env với thông tin database của bạn
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=attendance_db

# Chạy server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test API
# Mở browser: http://localhost:8000/docs
```

**Endpoints chính:**
- `POST /api/auth/login` - Đăng nhập
- `GET /api/employees` - Danh sách nhân viên
- `GET /api/attendance/employee/{id}` - Lịch sử điểm danh
- `POST /api/faceid/scan` - Nhận diện khuôn mặt

### 4️⃣ **AI Model Training**

```powershell
# Di chuyển vào thư mục AI
cd D:\DACN\DACN\AI

# Chuẩn bị training data
# Tạo thư mục face_data/ với cấu trúc:
# face_data/
#   Thai/
#     img001.jpg
#     img002.jpg
#     ...
#   Huy/
#     img001.jpg
#     ...

# Train model
python train_best_model.py

# Kết quả:
# - faceid_best_model.pkl
# - faceid_best_model_metadata.pkl

# Update embeddings vào database
python update_embeddings_best_model.py
```

**Lưu ý Training:**
- Cần 30-50 ảnh/người để đạt accuracy cao
- Ảnh đa dạng: góc độ, ánh sáng, biểu cảm
- Kích thước ảnh tối thiểu: 300x300
- Format: JPG, PNG

### 5️⃣ **Desktop App (Face Recognition)**

```powershell
# Install dependencies
cd D:\DACN\DACN\faceid_desktop
pip install -r requirements.txt

# Lưu ý: dlib cần Visual Studio Build Tools
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Copy .env
cp .env.example .env

# Chỉnh sửa .env với thông tin của bạn
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=attendance_db

# Chạy app
python main.py

# Hoặc với venv từ root
D:\DACN\.venv\Scripts\python.exe main.py
```

**Cách sử dụng:**
1. Nhấn "BẬT CAMERA"
2. Nhìn thẳng vào camera
3. Hệ thống tự động nhận diện và điểm danh
4. Kết quả hiển thị trên màn hình

### 6️⃣ **Mobile App (React Native + Expo)**

```bash
# Install dependencies
cd DACN/mobile_app
npm install

# Hoặc với yarn
yarn install

# Cấu hình backend URL
# Chỉnh sửa config.js:
export const API_BASE_URL = "http://192.168.x.x:8000";  # IP máy chạy backend

# Chạy app
npx expo start

# Scan QR code bằng Expo Go app (iOS/Android)
# Hoặc nhấn 'a' (Android), 'i' (iOS), 'w' (Web)
```

**Tính năng:**
- Đăng nhập nhân viên
- Xem lịch sử điểm danh
- Thống kê đúng giờ/trễ
- Cập nhật thông tin cá nhân

### 7️⃣ **Admin Web (ASP.NET Core)**

```powershell
# Build project
cd D:\DACN\DACN
dotnet restore
dotnet build

# Chạy web server
dotnet run

# Hoặc
dotnet watch run  # Auto reload khi code thay đổi

# Mở browser: https://localhost:5001
```

**Chức năng Admin:**
- Quản lý nhân viên
- Quản lý ca làm việc
- Xem báo cáo điểm danh
- Quản lý thiết bị
- Quản lý users

---

## 🎯 WORKFLOW SỬ DỤNG

### **Scenario 1: Nhân viên điểm danh**

1. **Desktop App (Tại văn phòng):**
   - Nhân viên đến văn phòng
   - Mở Desktop App
   - Nhìn vào camera → Tự động nhận diện
   - Hệ thống lưu điểm danh + tạo ca làm việc

2. **Mobile App (Kiểm tra):**
   - Nhân viên mở app
   - Xem lịch sử điểm danh
   - Kiểm tra thống kê tháng

### **Scenario 2: Admin quản lý**

1. **Admin Web:**
   - Đăng nhập admin panel
   - Xem danh sách điểm danh hôm nay
   - Export báo cáo Excel
   - Thêm/sửa thông tin nhân viên
   - Quản lý ca làm việc

### **Scenario 3: Thêm nhân viên mới**

1. **Thu thập training data:**
   ```bash
   # Tạo folder
   mkdir DACN/AI/face_data/TenNhanVien
   
   # Chụp 30-50 ảnh khuôn mặt
   # Đa dạng góc độ, ánh sáng
   ```

2. **Train lại model:**
   ```bash
   cd DACN/AI
   python train_best_model.py
   ```

3. **Update database:**
   ```bash
   python update_embeddings_best_model.py
   ```

4. **Test với Desktop App**

---

## 🐛 TROUBLESHOOTING

### **Backend không start được**

```powershell
# Kiểm tra port 8000 có bị chiếm không
netstat -ano | findstr :8000

# Kill process nếu cần
taskkill /PID <PID> /F

# Kiểm tra database connection
mysql -u root -p -e "SHOW DATABASES;"
```

### **Desktop App không nhận diện được**

1. **Kiểm tra model files:**
   ```bash
   ls DACN/AI/faceid_best_model.pkl
   ls DACN/AI/faceid_best_model_metadata.pkl
   ```

2. **Kiểm tra camera:**
   ```python
   import cv2
   cap = cv2.VideoCapture(0)
   print(cap.isOpened())  # Should be True
   ```

3. **Kiểm tra training data:**
   - Cần tối thiểu 2 ảnh/người
   - Ảnh phải rõ nét, có khuôn mặt

### **Mobile App không kết nối được backend**

1. **Kiểm tra IP:**
   ```bash
   # Trên máy chạy backend
   ipconfig  # Windows
   ifconfig  # Linux/Mac
   ```

2. **Kiểm tra firewall:**
   - Allow port 8000
   - Tắt firewall để test

3. **Kiểm tra config.js:**
   ```javascript
   // Phải dùng IP local, không phải localhost
   export const API_BASE_URL = "http://192.168.1.100:8000";
   ```

### **Dlib install failed (Windows)**

```powershell
# Install Visual Studio Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Sau đó install dlib
pip install dlib

# Nếu vẫn lỗi, dùng pre-built wheel
pip install dlib-19.24.0-cp310-cp310-win_amd64.whl
```

### **Low AI accuracy (<70%)**

**Nguyên nhân:**
- Thiếu training data
- Ảnh chất lượng kém
- Ánh sáng không đồng đều

**Giải pháp:**
1. Thu thập 30-50 ảnh/người
2. Chụp với ánh sáng tốt
3. Đa dạng góc độ ±30°
4. Retrain model
5. Tăng threshold lên 0.60-0.70

---

## 📊 MONITORING & LOGS

### **Backend logs**
```bash
# Loguru tự động log ra file
tail -f backend_src/logs/app.log
```

### **Database queries**
```sql
-- Kiểm tra điểm danh hôm nay
SELECT e.name, ar.timestamp_in, ar.status 
FROM attendance_records ar
JOIN employees e ON ar.employee_id = e.id
WHERE DATE(ar.timestamp_in) = CURDATE();

-- Thống kê theo tháng
SELECT e.name, COUNT(*) as days
FROM attendance_records ar
JOIN employees e ON ar.employee_id = e.id
WHERE MONTH(ar.timestamp_in) = MONTH(CURDATE())
GROUP BY e.id;
```

### **API Health Check**
```bash
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "redis": false,
#   "timestamp": "2025-11-14T08:30:00",
#   "version": "1.3.0"
# }
```

---

## 🎓 BEST PRACTICES

### **Security**
- [ ] Đổi password database mặc định
- [ ] Sử dụng HTTPS cho production
- [ ] Rate limiting enabled
- [ ] JWT token expiration: 24 hours
- [ ] Sanitize input data

### **Performance**
- [ ] Desktop app: Detect face mỗi 0.5s (không phải mỗi frame)
- [ ] Backend: Connection pooling enabled
- [ ] Mobile: Implement pagination cho attendance list
- [ ] Cache static data (employees list)

### **Data Management**
- [ ] Backup database hàng ngày
- [ ] Rotate logs tự động (500MB/file)
- [ ] Export attendance reports định kỳ
- [ ] Clean old attendance records (>1 năm)

### **Code Quality**
- [ ] Write unit tests (target: 70% coverage)
- [ ] Code review trước khi merge
- [ ] Follow PEP 8 (Python), Airbnb (JavaScript)
- [ ] Comment code phức tạp

---

## 📞 SUPPORT

**Issues:** GitHub Issues  
**Documentation:** README.md trong mỗi folder  
**API Docs:** http://localhost:8000/docs  

**Team:**
- Backend: FastAPI + Python
- Mobile: React Native + Expo
- Desktop: PySide6 + Python
- Admin: ASP.NET Core + C#
- AI: face_recognition + scikit-learn

---

**Cập nhật lần cuối:** 14/11/2025  
**Phiên bản hệ thống:** 1.0.0  
**Trạng thái:** ✅ Production Ready (sau khi fix training data)
