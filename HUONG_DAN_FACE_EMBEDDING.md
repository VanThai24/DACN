# 🎯 Hướng dẫn xử lý Face Embedding khi thêm nhân viên

## 📋 Tổng quan

Khi Admin thêm nhân viên mới vào hệ thống qua AdminWeb, có 3 kịch bản có thể xảy ra:

### ✅ Kịch bản 1: Thành công hoàn toàn
**Điều kiện:** Backend API đang chạy trên port 8000 và ảnh nhân viên rõ mặt

**Kết quả:**
- ✅ Nhân viên được tạo trong database
- ✅ Face embedding được lưu vào cột `face_embedding`
- ✅ Tài khoản User được tạo (username = số điện thoại, password = 123456)
- ✅ Email thông báo được gửi
- ✅ Thông báo màu **XANH**: "Thêm nhân viên thành công, đã gửi email thông báo!"

### ⚠️ Kịch bản 2: Thành công nhưng không có Face ID
**Điều kiện:** Backend API KHÔNG chạy hoặc ảnh không nhận diện được khuôn mặt

**Kết quả:**
- ✅ Nhân viên được tạo trong database
- ❌ Face embedding = NULL
- ✅ Tài khoản User được tạo
- ✅ Email thông báo được gửi
- ⚠️ Thông báo màu **VÀNG**: "Không thể kết nối Backend API (port 8000). Nhân viên được tạo nhưng chưa có Face ID. Hãy chạy Backend API và thử lại."

### ❌ Kịch bản 3: Thất bại hoàn toàn
**Điều kiện:** Lỗi database, validation, hoặc lỗi hệ thống

**Kết quả:**
- ❌ Nhân viên KHÔNG được tạo
- ❌ Không có thay đổi nào trong database
- ❌ Thông báo màu **ĐỎ**: "Thêm nhân viên thất bại: [chi tiết lỗi]"

---

## 🔧 Cách khắc phục khi không có Face Embedding

### Bước 1: Khởi động Backend API

```powershell
# Mở terminal mới tại D:\DACN
cd D:\DACN

# Kích hoạt virtual environment (nếu chưa)
.venv\Scripts\activate

# Chạy Backend API
.venv\Scripts\python.exe -m uvicorn backend_src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Kiểm tra Backend đã chạy: Mở browser vào http://localhost:8000/docs

### Bước 2: Upload lại ảnh cho nhân viên

Có 2 cách:

#### Cách 1: Qua AdminWeb (Khuyến nghị)
1. Vào **Quản lý Nhân viên** → Tìm nhân viên cần cập nhật
2. Click nút **Sửa** (icon bút chì màu hồng)
3. Upload ảnh mới (ảnh rõ mặt, nhìn thẳng, ánh sáng tốt)
4. Click **Lưu**
5. Kiểm tra xem có badge "Có Face ID" (màu xanh) không

#### Cách 2: Qua Backend API trực tiếp
```bash
curl -X POST "http://localhost:8000/api/faceid/add_face" \
  -F "image=@path/to/photo.jpg" \
  -F "name=Nguyen Van A"
```

### Bước 3: Xác nhận thành công

Vào trang **Quản lý khuôn mặt** để kiểm tra:
- Nhân viên xuất hiện trong danh sách
- Avatar hiển thị đúng
- Badge "Có Face ID" màu xanh

---

## 🎨 Màu sắc thông báo

| Màu | Loại | Icon | Ý nghĩa |
|-----|------|------|---------|
| 🟢 Xanh | Success | ✓ | Thành công hoàn toàn |
| 🟡 Vàng | Warning | ⚠ | Thành công nhưng có vấn đề nhỏ |
| 🔴 Đỏ | Error | ✗ | Thất bại hoàn toàn |

---

## 📝 Các thông báo Warning phổ biến

### 1. "Không thể kết nối Backend API (port 8000)"
**Nguyên nhân:** Backend API chưa khởi động

**Giải pháp:** 
```powershell
.venv\Scripts\python.exe -m uvicorn backend_src.app.main:app --host 0.0.0.0 --port 8000
```

### 2. "Không nhận diện được khuôn mặt"
**Nguyên nhân:** 
- Ảnh mờ hoặc tối
- Khuôn mặt bị che khuất
- Góc chụp nghiêng quá nhiều
- Nhiều người trong ảnh

**Giải pháp:** Upload ảnh mới với yêu cầu:
- ✅ Nhìn thẳng camera
- ✅ Ánh sáng đủ
- ✅ Chỉ 1 người trong ảnh
- ✅ Khuôn mặt rõ nét, không đeo kính đen/khẩu trang

### 3. "Backend API phản hồi quá chậm"
**Nguyên nhân:** API timeout sau 10 giây

**Giải pháp:**
- Kiểm tra Backend API có đang xử lý request khác không
- Restart Backend API
- Kiểm tra tài nguyên máy (CPU, RAM)

### 4. "Lỗi xử lý ảnh khuôn mặt"
**Nguyên nhân:** Lỗi không xác định từ API

**Giải pháp:**
- Xem log Backend API: `uvicorn` terminal sẽ hiển thị lỗi chi tiết
- Kiểm tra format ảnh (chỉ hỗ trợ JPG, PNG)
- Kiểm tra kích thước ảnh (< 5MB)

---

## 🔍 Debug và Logging

### Xem log AdminWeb
```powershell
# Log sẽ hiển thị trong terminal đang chạy `dotnet run`
```

Log sẽ có dạng:
```
info: Controllers.EmployeesController[0]
      Successfully extracted face embedding for Nguyen Van A
```

### Xem log Backend API
```powershell
# Log sẽ hiển thị trong terminal đang chạy uvicorn
```

Log sẽ có dạng:
```
INFO:     POST /api/faceid/add_face 200 OK
```

### Kiểm tra database trực tiếp

```sql
-- Xem nhân viên có face embedding
SELECT id, name, 
       CASE WHEN face_embedding IS NULL THEN 'NO' ELSE 'YES' END as has_face
FROM employees;

-- Đếm nhân viên có/không có face
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN face_embedding IS NOT NULL THEN 1 ELSE 0 END) as has_face,
    SUM(CASE WHEN face_embedding IS NULL THEN 1 ELSE 0 END) as no_face
FROM employees;
```

---

## 🚀 Best Practices

### Khi thêm nhân viên mới:
1. ✅ **BẮT BUỘC**: Chạy Backend API trước
2. ✅ Chuẩn bị ảnh đúng chuẩn (rõ mặt, 1 người, ánh sáng tốt)
3. ✅ Điền đầy đủ thông tin: Tên, SĐT, Email, Phòng ban
4. ✅ Kiểm tra thông báo sau khi thêm
5. ✅ Nếu có warning, xử lý ngay (upload lại ảnh)

### Quy trình chuẩn:
```
1. Start Backend API (port 8000)
2. Start AdminWeb (port 5280)
3. Login với tài khoản Admin
4. Thêm nhân viên với ảnh rõ mặt
5. Kiểm tra thông báo (xanh = OK, vàng = cần xử lý)
6. Vào "Quản lý khuôn mặt" để xác nhận
```

---

## ⚡ Troubleshooting nhanh

| Vấn đề | Giải pháp |
|--------|-----------|
| Backend API không khởi động | Kiểm tra port 8000 có bị chiếm không: `netstat -ano \| findstr :8000` |
| Ảnh không upload được | Kiểm tra thư mục `wwwroot/photos` có quyền ghi không |
| Email không gửi | Cấu hình SMTP trong `EmployeesController.cs` (hiện đang skip lỗi email) |
| Face embedding = NULL | Upload lại ảnh qua chức năng "Sửa nhân viên" |
| User không tạo được | Kiểm tra SĐT đã tồn tại chưa trong bảng `users` |

---

**Cập nhật:** 12/11/2025  
**Tác giả:** DACN Team
