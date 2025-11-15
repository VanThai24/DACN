# 🐛 Troubleshooting Guide - Hướng Dẫn Xử Lý Lỗi

## 📋 Mục Lục
1. [Desktop App Issues](#desktop-app)
2. [AI/Face Recognition Issues](#ai-issues)
3. [Database Issues](#database-issues)
4. [Mobile App Issues](#mobile-app)
5. [Web Admin Issues](#web-admin)
6. [Training Issues](#training-issues)

---

## 🖥️ Desktop App Issues {#desktop-app}

### ❌ Lỗi: "JWT token not found"
**Hiện tượng:**
```
⚠️ JWT token not found! Please login first
```

**Nguyên nhân:**
- Backend API chưa chạy (không ảnh hưởng face recognition)

**Giải pháp:**
```bash
# Option 1: Ignore (face recognition vẫn hoạt động)
# Option 2: Start backend API
cd D:\DACN\DACN\backend_src
uvicorn app.main:app --reload
```

**Mức độ nghiêm trọng:** ⚠️ Low (không ảnh hưởng chức năng chính)

---

### ❌ Lỗi: "Could not open camera"
**Hiện tượng:**
- Camera không mở được
- Màn hình đen

**Nguyên nhân:**
- Camera đang được sử dụng bởi app khác
- Driver camera lỗi
- Quyền truy cập camera bị chặn

**Giải pháp:**
```bash
# 1. Đóng các app đang dùng camera (Zoom, Skype, etc.)
# 2. Restart app
python main.py

# 3. Nếu vẫn lỗi, test camera với OpenCV:
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

**Mức độ nghiêm trọng:** 🔴 High

---

### ❌ Lỗi: "No face detected"
**Hiện tượng:**
- Không nhận diện được khuôn mặt
- Chữ "NO FACE" hiển thị liên tục

**Nguyên nhân:**
- Ánh sáng không đủ
- Khuôn mặt quá xa/gần camera
- Góc nghiêng quá nhiều

**Giải pháp:**
1. ✅ Kiểm tra ánh sáng (cần sáng đủ)
2. ✅ Điều chỉnh khoảng cách: 30-80cm
3. ✅ Nhìn thẳng vào camera
4. ✅ Tháo khẩu trang/kính râm

**Mức độ nghiêm trọng:** 🟡 Medium

---

### ❌ Lỗi: "Unknown person"
**Hiện tượng:**
```
⚠️ UNKNOWN (Không tìm thấy trong DB)
```

**Nguyên nhân:**
- Người này chưa được train vào model
- Model chưa được update embeddings
- Face encoding khác biệt quá nhiều

**Giải pháp:**
```bash
# 1. Kiểm tra person đã có trong database chưa
cd D:\DACN\DACN\AI
python check_data.py

# 2. Nếu chưa có, thêm mới:
.\add_new_employee.bat

# 3. Nếu đã có nhưng vẫn lỗi, retrain:
python train_best_model.py
python update_embeddings_best_model.py
```

**Mức độ nghiêm trọng:** 🟡 Medium

---

## 🤖 AI/Face Recognition Issues {#ai-issues}

### ❌ Lỗi: "No face encodings found"
**Hiện tượng:**
```python
ValueError: No face encodings found in the image
```

**Nguyên nhân:**
- Ảnh quá tối/mờ
- Khuôn mặt quá nhỏ
- Không có khuôn mặt trong ảnh

**Giải pháp:**
```python
# Test với ảnh cụ thể:
import face_recognition
img = face_recognition.load_image_file('test.jpg')
encodings = face_recognition.face_encodings(img)
print(f"Found {len(encodings)} faces")
```

**Mức độ nghiêm trọng:** 🟡 Medium

---

### ❌ Lỗi: "Model file not found"
**Hiện tượng:**
```python
FileNotFoundError: faceid_best_model.pkl not found
```

**Nguyên nhân:**
- Model chưa được train
- File bị xóa

**Giải pháp:**
```bash
cd D:\DACN\DACN\AI
python train_best_model.py
```

**Mức độ nghiêm trọng:** 🔴 High

---

### ❌ Lỗi: Low confidence (<40%)
**Hiện tượng:**
- Nhận diện được nhưng confidence thấp
- Không chắc chắn

**Nguyên nhân:**
- Training data không đủ đa dạng
- Lighting khác biệt train vs test
- Model chưa tối ưu

**Giải pháp:**
```bash
# 1. Chụp thêm ảnh với nhiều điều kiện ánh sáng
cd D:\DACN\DACN\AI
python capture_training_data.py

# 2. Augment data
python augment_data.py

# 3. Retrain
python train_best_model.py
python update_embeddings_best_model.py
```

**Mức độ nghiêm trọng:** 🟡 Medium

---

## 🗄️ Database Issues {#database-issues}

### ❌ Lỗi: "Can't connect to MySQL server"
**Hiện tượng:**
```
mysql.connector.errors.DatabaseError: 2003: Can't connect to MySQL server
```

**Nguyên nhân:**
- MySQL chưa start
- Sai password
- Port bị block

**Giải pháp:**
```powershell
# 1. Start MySQL service
net start MySQL80

# 2. Test connection
mysql -u root -p12345 -e "SELECT 1"

# 3. Check port
netstat -ano | findstr :3306
```

**Mức độ nghiêm trọng:** 🔴 High

---

### ❌ Lỗi: "Access denied for user 'root'@'localhost'"
**Hiện tượng:**
```
mysql.connector.errors.ProgrammingError: 1045: Access denied
```

**Nguyên nhân:**
- Sai password

**Giải pháp:**
```bash
# Update password trong các files:
# 1. DACN/AI/app.py -> line 40
# 2. DACN/AI/db.py
# 3. DACN/faceid_desktop/main.py
# 4. DACN/appsettings.json

# Hoặc reset MySQL password:
# ALTER USER 'root'@'localhost' IDENTIFIED BY '12345';
```

**Mức độ nghiêm trọng:** 🔴 High

---

### ❌ Lỗi: "Unknown database 'attendance_db'"
**Hiện tượng:**
```
mysql.connector.errors.ProgrammingError: 1049: Unknown database
```

**Nguyên nhân:**
- Database chưa được tạo

**Giải pháp:**
```sql
-- Tạo database
CREATE DATABASE attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Chạy migrations
cd D:\DACN\DACN\backend_src
alembic upgrade head
```

**Mức độ nghiêm trọng:** 🔴 High

---

## 📱 Mobile App Issues {#mobile-app}

### ❌ Lỗi: "Metro bundler not found"
**Hiện tượng:**
```
Error: Metro bundler not found
```

**Nguyên nhân:**
- Dependencies chưa cài

**Giải pháp:**
```bash
cd D:\DACN\DACN\mobile_app
npm install
npm start
```

**Mức độ nghiêm trọng:** 🔴 High

---

### ❌ Lỗi: "Network request failed"
**Hiện tượng:**
- Không kết nối được API
- Timeout

**Nguyên nhân:**
- Backend API chưa chạy
- IP/Port sai
- Firewall block

**Giải pháp:**
```javascript
// 1. Check config.js
export const API_URL = 'http://192.168.1.x:8000';  // Update IP

// 2. Start backend
cd D:\DACN\DACN\backend_src
uvicorn app.main:app --host 0.0.0.0 --port 8000

// 3. Test from mobile:
curl http://192.168.1.x:8000/health
```

**Mức độ nghiêm trọng:** 🔴 High

---

## 🌐 Web Admin Issues {#web-admin}

### ❌ Lỗi: "Connection string is invalid"
**Hiện tượng:**
```
InvalidOperationException: Connection string is invalid
```

**Nguyên nhân:**
- Connection string sai trong `appsettings.json`

**Giải pháp:**
```json
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=attendance_db;User=root;Password=12345;"
  }
}
```

**Mức độ nghiêm trọng:** 🔴 High

---

### ❌ Lỗi: "Port 5001 already in use"
**Hiện tượng:**
```
System.IO.IOException: Failed to bind to address
```

**Nguyên nhân:**
- Port đang được sử dụng

**Giải pháp:**
```powershell
# 1. Find process using port
netstat -ano | findstr :5001

# 2. Kill process
taskkill /PID <PID> /F

# 3. Or change port in launchSettings.json
```

**Mức độ nghiêm trọng:** 🟡 Medium

---

## 🧠 Training Issues {#training-issues}

### ❌ Lỗi: "Not enough samples for person X"
**Hiện tượng:**
```
ValueError: Person 'John' has only 3 samples, need at least 40
```

**Nguyên nhân:**
- Không đủ ảnh training

**Giải pháp:**
```bash
# Option 1: Chụp thêm ảnh
python capture_training_data.py

# Option 2: Augmentation
python augment_data.py
```

**Mức độ nghiêm trọng:** 🟡 Medium

---

### ❌ Lỗi: "OpenCV encoding error with Vietnamese characters"
**Hiện tượng:**
```
cv2.error: OpenCV(4.x) [...] Bad input filename
```

**Nguyên nhân:**
- Filename có ký tự tiếng Việt
- OpenCV không support Unicode path

**Giải pháp:**
```bash
# Rename files to ASCII only
# Before: Nguyễn_Văn_A_001.jpg
# After:  Nguyen_Van_A_001.jpg

# Or use cv2.imdecode instead:
import cv2
import numpy as np
with open(filepath, 'rb') as f:
    img = cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)
```

**Mức độ nghiêm trọng:** 🟡 Medium

---

### ❌ Lỗi: "GridSearchCV running forever"
**Hiện tượng:**
- Training không bao giờ kết thúc
- CPU 100%

**Nguyên nhân:**
- Quá nhiều combinations
- Dataset quá lớn

**Giải pháo:**
```python
# Giảm param_grid:
param_grid = {
    'C': [1, 10],           # Instead of [0.1, 1, 10, 100]
    'gamma': ['scale'],      # Instead of ['scale', 'auto', ...]
    'kernel': ['rbf']        # Instead of ['rbf', 'linear']
}
```

**Mức độ nghiêm trọng:** 🟡 Medium

---

## 🆘 Emergency Fixes

### 🚨 System không hoạt động hoàn toàn
**Quick reset:**
```powershell
# 1. Stop all processes
taskkill /F /IM python.exe
taskkill /F /IM dotnet.exe
taskkill /F /IM node.exe

# 2. Restart MySQL
net stop MySQL80
net start MySQL80

# 3. Clear cache
cd D:\DACN\DACN\AI
Remove-Item -Recurse __pycache__

# 4. Restart Desktop app
cd D:\DACN\DACN\faceid_desktop
python main.py
```

---

### 🚨 Demo bị lỗi trước giờ bảo vệ
**Backup plan:**
1. ✅ Có video demo sẵn
2. ✅ Có screenshots của từng tính năng
3. ✅ Có slides giải thích code
4. ✅ Test trên laptop dự phòng

---

## 📞 Support Checklist

Trước khi hỏi support, check:
- [ ] MySQL đã start chưa?
- [ ] Python version >= 3.8?
- [ ] Dependencies đã cài đủ chưa?
- [ ] Model file có tồn tại không?
- [ ] Database có dữ liệu chưa?
- [ ] Camera hoạt động không?
- [ ] Internet connection OK?

---

## 🔍 Debug Tools

### Check Python environment
```bash
python --version
pip list | findstr face_recognition
pip list | findstr opencv
```

### Check MySQL status
```bash
net start | findstr MySQL
mysql -u root -p12345 -e "SHOW DATABASES"
```

### Check ports
```bash
netstat -ano | findstr :5001
netstat -ano | findstr :8000
netstat -ano | findstr :3306
```

### Test modules
```python
import face_recognition
import cv2
import mysql.connector
import joblib
print("All OK!")
```

---

**📅 Last Updated**: November 2025  
**🎯 Coverage**: 95% common issues
