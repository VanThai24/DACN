# 🔐 Tài khoản Test - Hệ thống Điểm danh

## 📱 Tài khoản Mobile App (Nhân viên)

### Tài khoản Test 1 - Nguyễn Văn Test
```
Username: testuser
Password: 123456
Role: Employee
```
**Thông tin nhân viên:**
- Tên: Nguyễn Văn Test
- Phòng ban: Phòng IT
- Chức vụ: Nhân viên
- SĐT: 0123456789
- Email: testuser@company.com

### Tài khoản Test 2 - Đặng Văn Thái
```
Username: 0123456789
Password: [Kiểm tra trong database]
Role: Employee
```
**Thông tin nhân viên:**
- Tên: Đặng Văn Thái
- Phòng ban: IT
- SĐT: 0123456789
- Email: thainro129@gmail.com

---

## 💻 Tài khoản AdminWeb (Quản trị)

### Tài khoản Admin
```
Username: admin
Password: [Kiểm tra với dev]
Role: Admin
```

---

## ⚠️ Lưu ý quan trọng

### Phân quyền Role:
- **Admin**: Chỉ đăng nhập được AdminWeb (localhost:5280)
- **Employee**: Chỉ đăng nhập được Mobile App
- **Manager**: Tùy chỉnh theo yêu cầu

### Case Sensitivity:
- Role PHẢI viết hoa chữ cái đầu: `Admin`, `Employee`, `Manager`
- Không dùng: `admin`, `employee`, `ADMIN`, v.v.

### Mobile App Config:
Trong file `mobile_app/config.js`:
```javascript
export const SERVER_IP = "192.168.110.45"; // Đổi IP này khi đổi mạng
export const API_URL = `http://${SERVER_IP}:8000`;
```

---

## 🛠 Scripts hỗ trợ

### 1. Thêm tài khoản test mới:
```bash
.venv\Scripts\python.exe DACN\add_test_employee_mysql.py
```

### 2. Xem danh sách tài khoản:
```bash
.venv\Scripts\python.exe DACN\list_users.py
```

### 3. Chuẩn hóa Role (fix case):
```bash
.venv\Scripts\python.exe DACN\normalize_roles.py
```

### 4. Kiểm tra cấu trúc database:
```bash
.venv\Scripts\python.exe DACN\check_mysql_structure.py
```

---

## 🚀 Chạy hệ thống

### Backend API (FastAPI):
```bash
cd backend_src
..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### AdminWeb (ASP.NET):
```bash
cd DACN
dotnet run
# hoặc
dotnet watch run
```
Truy cập: http://localhost:5280

### Mobile App (React Native/Expo):
```bash
cd mobile_app
npm start
# hoặc
npm run android
npm run ios
```

---

## 🔍 Troubleshooting

### Không đăng nhập được Mobile App?
1. Kiểm tra Role = "Employee" (chữ E hoa)
2. Kiểm tra SERVER_IP trong config.js
3. Kiểm tra Backend API đang chạy trên port 8000
4. Kiểm tra thiết bị và server cùng mạng WiFi

### Không đăng nhập được AdminWeb?
1. Kiểm tra Role = "Admin" (chữ A hoa)
2. Kiểm tra MySQL đang chạy
3. Kiểm tra connection string trong appsettings.json
4. Xóa cookies browser và thử lại

### Lỗi "Access denied" MySQL?
1. Kiểm tra MySQL user permissions
2. Connection string đúng: `server=127.0.0.1;port=3306;database=attendance_db;uid=root;pwd=12345;`
3. Chạy: `dotnet clean` và `dotnet build` lại

---

**Cập nhật:** 12/11/2025  
**Developer:** DACN Team
