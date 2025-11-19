# 🎓 Hệ Thống Điểm Danh Nhận Diện Khuôn Mặt

## 📋 Tổng Quan
Đồ án chuyên ngành: Hệ thống điểm danh tự động sử dụng công nghệ nhận diện khuôn mặt AI

### ⚡ Thông Số Kỹ Thuật
- **Thuật toán AI**: Face Recognition (dlib) + SVM Classifier
- **Độ chính xác**: 100% (Test Accuracy)
- **Thời gian xử lý**: <1s/khuôn mặt
- **Database**: MySQL 8.x
- **Số lượng ứng dụng**: 4 apps (Desktop, Mobile, Web Admin, API)

---

## 🏗️ Kiến Trúc Hệ Thống

```
📦 DACN/
├── 🖥️ DACN/                    # Main ASP.NET Core Web Admin
│   ├── Controllers/           # MVC Controllers
│   ├── Models/               # Entity Models
│   ├── Views/                # Razor Views
│   └── wwwroot/              # Static files
│
├── 🤖 AI/                      # Face Recognition System
│   ├── app.py                # Flask API Server
│   ├── train_best_model.py   # Model Training
│   ├── update_embeddings_best_model.py
│   ├── faceid_best_model.pkl # Trained SVM Model
│   └── face_data/            # Training Images
│
├── 🖥️ faceid_desktop/         # Desktop App (PySide6)
│   └── main.py               # GUI Application
│
├── 📱 mobile_app/             # React Native App
│   ├── screens/              # UI Screens
│   └── components/           # React Components
│
└── 🔧 backend_src/            # FastAPI Backend
    └── app/                  # API Endpoints
```

---

## 🚀 Quick Start

### 1️⃣ Chạy Desktop App (Khuyến Nghị)
```powershell
cd D:\DACN\DACN\faceid_desktop
python main.py
```
- Ấn **"BẬT CAMERA"** để mở webcam
- Ấn **SPACE** để điểm danh
- Hệ thống tự động nhận diện và ghi nhận

### 2️⃣ Chạy Web Admin
```powershell
cd D:\DACN\DACN
dotnet run
```
Mở browser: `https://localhost:5001`

### 3️⃣ Chạy Mobile App
```powershell
cd D:\DACN\DACN\mobile_app
npm start
```

---

## 👨‍💼 Quản Lý Nhân Viên

### ➕ Thêm Nhân Viên Mới
```powershell
cd D:\DACN\DACN\AI
.\add_new_employee.bat
```
**Quy trình tự động:**
1. Chụp 15-20 ảnh khuôn mặt (5 góc độ)
2. Tăng cường dữ liệu lên 40 ảnh
3. Huấn luyện lại model
4. Cập nhật embeddings vào database

⏱️ **Thời gian**: ~10 phút/nhân viên

### 📊 Kiểm Tra Dữ Liệu
```powershell
python check_data.py
```

---

## 🧠 AI Training Pipeline

### 🎯 Huấn Luyện Model
```powershell
cd D:\DACN\DACN\AI
python train_best_model.py
```

**Kết quả hiện tại:**
- ✅ Train Accuracy: 100%
- ✅ Test Accuracy: 100%
- ⚙️ Best Params: C=10, gamma='scale', kernel='rbf'
- 📊 Classes: 5 nhân viên
- 💪 Confidence: 58.61% ± 19.86%

### 🔄 Cập Nhật Embeddings
```powershell
python update_embeddings_best_model.py
```

---

## 📚 Tài Liệu Chi Tiết


### 📖 Hướng Dẫn Sử Dụng Báo Cáo
- Vào Web Admin, chọn chức năng xuất báo cáo điểm danh hoặc nhân viên.
- File báo cáo sẽ có tiêu đề lớn nổi bật, bảng dữ liệu rõ ràng.
- Khi mở file CSV bằng Excel:
  - Kéo rộng cột ngày giờ để hiển thị đầy đủ.
  - Số điện thoại sẽ hiển thị đúng định dạng, không bị chuyển sang số khoa học.
  - Có thể merge, bôi đậm, tăng cỡ chữ tiêu đề lớn để nổi bật hơn.

### 📑 Tính Năng Báo Cáo Mới
- Xuất báo cáo điểm danh/thông tin nhân viên với tiêu đề lớn, bảng dữ liệu chuẩn.
- Cột ngày giờ tách riêng, dễ đọc.
- Số điện thoại hiển thị đúng, không bị lỗi định dạng.

---

## 🔧 Cấu Hình

### Database (MySQL)
```sql
Host: localhost
User: root
Password: 12345
Database: attendance_db
```

### Tables
- `employees` - Thông tin nhân viên
- `attendance_records` - Lịch sử điểm danh
- `shifts` - Ca làm việc
- `users` - Tài khoản admin
- `devices` - Thiết bị đăng ký

---

## ⚠️ Lưu Ý Quan Trọng

### ✅ Đã Hoàn Thành
- ✅ Nhận diện khuôn mặt với độ chính xác 100%
- ✅ Ngăn chặn điểm danh trùng lặp trong cùng ca
- ✅ Tự động phát hiện ca làm việc
- ✅ 4 ứng dụng hoàn chỉnh
- ✅ Training pipeline tự động
- ✅ Data augmentation

### 🚧 Lưu Ý
- **Ánh sáng**: Cần đủ sáng để nhận diện chính xác
- **Khoảng cách**: 30-80cm từ camera
- **Góc nhìn**: Nhìn thẳng vào camera
- **Thêm nhân viên**: BẮT BUỘC phải train lại model

### 🐛 Troubleshooting
- **Không nhận diện được**: Kiểm tra ánh sáng, khoảng cách, train lại model
- **JWT Error**: Không ảnh hưởng face recognition, chỉ ảnh hưởng API
- **Lỗi encoding**: Tránh ký tự đặc biệt trong tên file ảnh

---

## 📞 Hỗ Trợ

### 📁 Files Quan Trọng
```
📂 AI/
  ├── app.py                           # Flask API
  ├── train_best_model.py              # Training
  ├── add_new_employee.py              # Thêm NV
  └── faceid_best_model.pkl            # Model file

📂 faceid_desktop/
  └── main.py                          # Desktop app

📂 mobile_app/
  └── App.js                           # Mobile app

📂 DACN/
  ├── Program.cs                       # Web admin
  ├── Controllers/AdminController.cs    # Chức năng xuất báo cáo
  └── wwwroot/reports/                  # Thư mục lưu file báo cáo
```

### 🎯 Mục Tiêu Đồ Án
- ✅ Xây dựng hệ thống điểm danh tự động
- ✅ Áp dụng AI/ML trong thực tế
- ✅ Tích hợp đa nền tảng (Web, Mobile, Desktop)
- ✅ Đáp ứng yêu cầu đồ án chuyên ngành

---

## 📊 Kết Quả Demo

### 🎥 Kịch Bản Demo
1. **Desktop App**: Mở camera → Nhận diện → Điểm danh thành công
2. **Web Admin**: Xem danh sách điểm danh → Thống kê
3. **Mobile App**: Xem lịch sử cá nhân → Dashboard

### 📈 Metrics
- ⚡ Thời gian nhận diện: <1s
- 🎯 Độ chính xác: 100%
- 🛡️ Bảo mật: JWT + BCrypt
- 🔄 Realtime: WebSocket ready

---

## 📜 License
Đồ án chuyên ngành - Chỉ cho mục đích học tập

---

## 🙏 Credits
- **Face Recognition**: dlib, face_recognition library
- **ML Framework**: scikit-learn
- **Backend**: FastAPI, ASP.NET Core
- **Mobile**: React Native + Expo
- **Desktop**: PySide6 (Qt)

---

**🎓 Version**: 1.0.0 (Thesis Edition)  
**📅 Last Updated**: November 2025  
**✍️ Author**: [Your Name]
