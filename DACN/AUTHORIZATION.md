# Hệ thống Phân quyền AdminWeb

## 🔒 Cơ chế phân quyền

### Vai trò (Roles)
1. **Admin** - Toàn quyền quản trị
2. **Manager** - Quản lý cấp trung
3. **User** (Nhân viên) - **KHÔNG CÓ QUYỀN** truy cập AdminWeb

### Quy tắc truy cập
- ✅ **Admin** và **Manager**: Được phép đăng nhập và truy cập đầy đủ AdminWeb
- ❌ **User** (Nhân viên): BỊ CHẶN khi đăng nhập, hiển thị thông báo:
  > "Bạn không có quyền truy cập hệ thống Admin!"

## 🛡️ Cơ chế bảo mật

### 1. BaseAdminController
Tất cả các controller kế thừa từ `BaseAdminController` để tự động kiểm tra:
```csharp
- Kiểm tra session "User" tồn tại
- Kiểm tra session "UserRole" là "Admin" hoặc "Manager"
- Redirect về /Account/Login nếu không đủ quyền
```

### 2. Session Management
Khi đăng nhập thành công, hệ thống lưu:
- `Session["User"]` - Username
- `Session["UserRole"]` - Role (Admin/Manager/User)
- `Session["UserId"]` - ID người dùng

### 3. Controller bảo vệ
Các controller sau được bảo vệ bởi BaseAdminController:
- ✅ AdminController
- ✅ AttendanceController  
- ✅ DevicesController
- ✅ ShiftsController
- ✅ EmployeesController
- ✅ UsersController

### 4. Controller công khai
- ✅ AccountController (Login/Logout) - Không yêu cầu authentication

## 📋 Flow đăng nhập

```
1. Người dùng nhập username/password
2. Kiểm tra username/password trong database
3. Kiểm tra Role:
   - Nếu Role = "User" → ❌ Chặn, hiển thị lỗi
   - Nếu Role = "Admin" hoặc "Manager" → ✅ Cho phép
4. Lưu session (User, UserRole, UserId)
5. Redirect về Dashboard
```

## 🎯 Sử dụng

### Tạo tài khoản Admin/Manager mới
Truy cập menu **Người dùng** → **Thêm người dùng**
- Chọn Role = "Admin" hoặc "Manager"
- Mật khẩu sẽ được hash tự động bằng BCrypt

### Kiểm tra quyền trong View
```razor
@Context.Session.GetString("UserRole")
```

### Hiển thị thông tin người dùng
Navbar hiển thị:
- Tên người dùng
- Role (Admin/Manager)

## ⚠️ Lưu ý quan trọng

1. **Nhân viên (User) không thể truy cập AdminWeb**
2. Chỉ Admin/Manager mới có thể:
   - Quản lý nhân viên
   - Quản lý điểm danh
   - Quản lý thiết bị
   - Tạo báo cáo
   - Quản lý người dùng

3. Mật khẩu được hash bằng BCrypt - không thể đọc được từ database

## 🔧 Cấu hình

File: `Controllers/BaseAdminController.cs`
```csharp
// Thay đổi logic phân quyền tại đây nếu cần
public override void OnActionExecuting(ActionExecutingContext context)
{
    var userRole = HttpContext.Session.GetString("UserRole");
    
    if (userRole != "Admin" && userRole != "Manager")
    {
        context.Result = new RedirectResult("/Account/Login");
    }
}
```

## 📱 Mobile App cho Nhân viên

Nhân viên sử dụng **Mobile App** (React Native) để:
- Điểm danh qua camera
- Xem lịch sử điểm danh
- Xem thông tin cá nhân

**Không** sử dụng AdminWeb!
