# 🔧 FIX LỖI "no such table: users" - Backend API đang dùng SQLite thay vì MySQL

## 🐛 Vấn đề:
```
ERROR: (sqlite3.OperationalError) no such table: users
Database engine created: sqlite:///./dacn.db
```

Backend API đang kết nối **SQLite** (file local) thay vì **MySQL** (server)

## ✅ Giải pháp đã áp dụng:

### File 1: `backend_src/.env`
```env
# TRƯỚC:
DATABASE_URL=sqlite:///./dacn.db

# SAU:
DATABASE_URL=mysql+mysqlconnector://root:12345@127.0.0.1:3306/attendance_db
```

### File 2: `backend_src/app/config.py`
```python
# TRƯỚC:
database_url: str = "sqlite:///./dacn.db"

# SAU:
database_url: str = "mysql+mysqlconnector://root:12345@127.0.0.1:3306/attendance_db"
```

## 🚀 Cách áp dụng:

**Bước 1:** Stop Backend API hiện tại
```
Nhấn Ctrl+C trong terminal
```

**Bước 2:** Restart Backend API
```powershell
cd D:\DACN\DACN
venv\Scripts\python.exe -m uvicorn backend_src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Bước 3:** Kiểm tra log khởi động
```
✅ ĐÚNG:
2025-11-12 19:25:00 | INFO | Database engine created: mysql+mysqlconnector://***@127.0.0.1:3306/attendance_db

❌ SAI:
2025-11-12 19:22:13 | INFO | Database engine created: sqlite:///./dacn.db
```

## 📊 Test kết nối:

**Test 1: Health Check**
```bash
curl http://192.168.110.29:8000/health
```

Kết quả mong đợi:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": false,
  "timestamp": "2025-11-12T19:25:00",
  "version": "1.3.0"
}
```

**Test 2: Login từ Mobile App**
```
Username: testuser
Password: 123456
```

Kết quả mong đợi:
```
✅ 200 OK - Đăng nhập thành công
```

## 🔍 Troubleshooting:

### Nếu vẫn lỗi "no such table":
1. Kiểm tra MySQL đang chạy
2. Kiểm tra database `attendance_db` tồn tại
3. Kiểm tra connection string đúng format

### Nếu lỗi "Access denied":
```bash
# Kiểm tra user/password MySQL
mysql -u root -p12345 -h 127.0.0.1
```

### Nếu vẫn load SQLite:
```bash
# Xóa cache Python
cd D:\DACN\DACN\backend_src
rm -r __pycache__
rm -r app/__pycache__

# Restart lại
```

---

**Fixed:** 12/11/2025 19:25  
**Status:** ✅ Ready to restart Backend API
