# 🎯 Hệ Thống Điểm Danh - Commands Cheat Sheet

## 🚀 Quick Commands

### Desktop App (Khuyến nghị)
```bash
cd D:\DACN\DACN\faceid_desktop
python main.py
```

### Web Admin
```bash
cd D:\DACN\DACN
dotnet run
# Mở browser: https://localhost:5001
```

### Mobile App
```bash
cd D:\DACN\DACN\mobile_app
npm start
# Ấn 'a' để mở Android emulator
```

### Backend API (FastAPI)
```bash
cd D:\DACN\DACN\backend_src
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧠 AI Training

### Kiểm tra dữ liệu
```bash
cd D:\DACN\DACN\AI
python check_data.py
```

### Train model mới
```bash
python train_best_model.py
```

### Update embeddings vào database
```bash
python update_embeddings_best_model.py
```

### Full pipeline (train + update)
```bash
python train_best_model.py && python update_embeddings_best_model.py
```

---

## 👨‍💼 Quản Lý Nhân Viên

### Thêm nhân viên mới (Auto)
```bash
cd D:\DACN\DACN\AI
.\add_new_employee.bat
```

### Chụp ảnh training manual
```bash
python capture_training_data.py
```

### Tăng cường dữ liệu (augmentation)
```bash
python augment_data.py
```

### Auto augment tất cả nhân viên
```bash
python auto_augment.py
```

---

## 🗄️ Database

### Kết nối MySQL
```bash
mysql -u root -p12345 attendance_db
```

### Xem danh sách nhân viên
```sql
SELECT id, name, face_encoding IS NOT NULL as has_embedding FROM employees;
```

### Xem điểm danh hôm nay
```sql
SELECT e.name, a.timestamp_in, s.name as shift 
FROM attendance_records a
JOIN employees e ON a.employee_id = e.id
JOIN shifts s ON a.shift_id = s.id
WHERE DATE(a.timestamp_in) = CURDATE();
```

### Xóa dữ liệu test
```sql
DELETE FROM attendance_records WHERE DATE(timestamp_in) = CURDATE();
```

---

## 🔧 Setup & Installation

### Cài đặt Python dependencies
```bash
cd D:\DACN\DACN\AI
pip install -r requirements.txt
```

### Cài đặt Mobile dependencies
```bash
cd D:\DACN\DACN\mobile_app
npm install
```

### Build Web Admin
```bash
cd D:\DACN\DACN
dotnet build
```

---

## 🧹 Dọn dẹp

### Xóa __pycache__
```bash
cd D:\DACN\DACN\AI
Remove-Item -Recurse -Force __pycache__
```

### Xóa logs
```bash
cd D:\DACN\DACN
Remove-Item -Recurse -Force logs\*
```

### Reset database (cẩn thận!)
```sql
TRUNCATE TABLE attendance_records;
```

---

## 🐛 Troubleshooting

### Fix JWT error trong Desktop app
```bash
# Start backend API trước
cd D:\DACN\DACN\backend_src
uvicorn app.main:app --reload
```

### Fix module not found
```bash
pip install face_recognition dlib opencv-python scikit-learn
```

### Fix MySQL connection error
```bash
# Check MySQL đang chạy
net start MySQL80

# Test connection
mysql -u root -p12345 -e "SELECT 1"
```

### Fix Vietnamese character trong filename
```bash
# Rename files to ASCII only
cd D:\DACN\DACN\AI\face_data\<folder>
# Rename manually or use Python script
```

---

## 📊 Testing

### Test face recognition
```bash
cd D:\DACN\DACN\AI
python -c "import face_recognition; print('OK')"
```

### Test model loading
```bash
python -c "import joblib; m = joblib.load('faceid_best_model.pkl'); print('OK')"
```

### Test database connection
```bash
python -c "import mysql.connector; mysql.connector.connect(host='localhost', user='root', password='12345', database='attendance_db'); print('OK')"
```

---

## 📱 Mobile App - Expo Commands

### Start development server
```bash
npm start
```

### Run on Android
```bash
npm run android
```

### Run on iOS (Mac only)
```bash
npm run ios
```

### Clear cache
```bash
expo start -c
```

---

## 🎯 Demo Workflow

### 1. Chuẩn bị
```bash
# Start MySQL
net start MySQL80

# Optional: Start backend API
cd D:\DACN\DACN\backend_src
uvicorn app.main:app --reload
```

### 2. Demo Desktop App
```bash
cd D:\DACN\DACN\faceid_desktop
python main.py
# Ấn "BẬT CAMERA" > SPACE để điểm danh
```

### 3. Xem kết quả trên Web
```bash
cd D:\DACN\DACN
dotnet run
# Browser: https://localhost:5001
```

### 4. Xem trên Mobile App
```bash
cd D:\DACN\DACN\mobile_app
npm start
# Ấn 'a' cho Android
```

---

## 🔑 Credentials

### Database
- Host: `localhost`
- User: `root`
- Password: `12345`
- Database: `attendance_db`

### Web Admin
- URL: `https://localhost:5001`
- Username: `admin`
- Password: `admin123`

### Mobile API
- URL: `http://localhost:8000`
- Token: JWT (auto-generated)

---

## 📦 Backup & Restore

### Backup model
```bash
cd D:\DACN\DACN\AI
copy faceid_best_model.pkl faceid_best_model_backup.pkl
copy faceid_best_model_metadata.pkl faceid_best_model_metadata_backup.pkl
```

### Backup database
```bash
mysqldump -u root -p12345 attendance_db > backup.sql
```

### Restore database
```bash
mysql -u root -p12345 attendance_db < backup.sql
```

---

## 🎓 Thesis Tips

### Demo sequence
1. Giải thích system architecture
2. Show Desktop app face recognition
3. Show Web admin attendance records
4. Show Mobile app user interface
5. Add new employee demo
6. Show model training process

### Important points
- ✅ 100% accuracy achieved
- ✅ Real-time processing (<1s)
- ✅ Multi-platform support
- ✅ Duplicate prevention
- ✅ Auto shift detection

### Backup plan
- Video demo nếu camera lỗi
- Screenshots của features chính
- Code walkthrough ready

---

**🎯 Version**: 1.0.0  
**📅 Last Updated**: November 2025
