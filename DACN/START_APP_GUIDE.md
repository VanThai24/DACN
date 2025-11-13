## 🚀 HƯỚNG DẪN CHẠY APP - FIX TRIỆT ĐỂ

### ❗ VẤN ĐỀ HIỆN TẠI:
- Lỗi 404 cho `/Attendance` và `/Users`
- **NGUYÊN NHÂN:** App chưa được chạy hoặc đang chạy code cũ

### ✅ GIẢI PHÁP:

#### Bước 1: Kiểm tra xem có process dotnet nào đang chạy không
```powershell
Get-Process dotnet -ErrorAction SilentlyContinue
```

#### Bước 2: Dừng tất cả process dotnet cũ (nếu có)
```powershell
Stop-Process -Name dotnet -Force -ErrorAction SilentlyContinue
```

#### Bước 3: Build lại project để apply changes
```powershell
cd D:\DACN\DACN
dotnet clean
dotnet build
```

#### Bước 4: Chạy app với Development mode để xem logs
```powershell
cd D:\DACN\DACN
$env:ASPNETCORE_ENVIRONMENT="Development"
dotnet run --urls "http://localhost:5280"
```

#### Bước 5: Mở browser và test
```
http://localhost:5280/Admin/Dashboard
http://localhost:5280/Users/Index
http://localhost:5280/Attendance/Index
```

---

## 🔍 KIỂM TRA NHANH

Chạy lệnh này để verify Program.cs đúng:
```powershell
Select-String -Path "D:\DACN\DACN\Program.cs" -Pattern "MapControllerRoute"
```

**Expected output:**
```
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Admin}/{action=Dashboard}/{id?}")
    .WithStaticAssets();
```

---

## 🐛 NẾU VẪN LỖI 404

### Debug Steps:

1. **Kiểm tra Console Output:**
   Khi chạy `dotnet run`, xem có error message không

2. **Kiểm tra Controllers:**
   ```powershell
   Get-ChildItem D:\DACN\DACN\Controllers\*.cs | Select-Object Name
   ```
   
   **Expected:**
   - AccountController.cs
   - AdminController.cs
   - AttendanceController.cs ✓
   - BaseAdminController.cs
   - DevicesController.cs
   - EmployeesController.cs
   - HomeController.cs
   - ShiftsController.cs
   - UsersController.cs ✓

3. **Kiểm tra Views:**
   ```powershell
   Get-ChildItem D:\DACN\DACN\Views\Attendance\*.cshtml | Select-Object Name
   Get-ChildItem D:\DACN\DACN\Views\Users\*.cshtml | Select-Object Name
   ```

4. **Test với curl (trong PowerShell):**
   ```powershell
   # Test sau khi app đã chạy
   curl http://localhost:5280/Users/Index -UseBasicParsing
   curl http://localhost:5280/Attendance/Index -UseBasicParsing
   ```

---

## ⚡ QUICK FIX SCRIPT

Copy paste và chạy tất cả lệnh này:

```powershell
# Stop old processes
Stop-Process -Name dotnet -Force -ErrorAction SilentlyContinue

# Navigate to project
cd D:\DACN\DACN

# Clean and rebuild
dotnet clean
dotnet build

# Run in Development mode
$env:ASPNETCORE_ENVIRONMENT="Development"
dotnet run --urls "http://localhost:5280"
```

---

## 📊 EXPECTED CONSOLE OUTPUT

Khi chạy `dotnet run`, bạn sẽ thấy:

```
Building...
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:5280
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
info: Microsoft.Hosting.Lifetime[0]
      Hosting environment: Development
info: Microsoft.Hosting.Lifetime[0]
      Content root path: D:\DACN\DACN
```

**Nếu thấy lỗi compilation hoặc runtime error, copy paste lỗi đó cho tôi!**

---

## ✅ SAU KHI APP CHẠY THÀNH CÔNG

Test tất cả routes này (trong browser hoặc bằng F12 Network tab):

- ✅ http://localhost:5280/ → Redirect to /Admin/Dashboard
- ✅ http://localhost:5280/Admin/Dashboard
- ✅ http://localhost:5280/Employees/Index
- ✅ http://localhost:5280/Devices/Index
- ✅ http://localhost:5280/Attendance/Index ← **MUST WORK**
- ✅ http://localhost:5280/Shifts/Index
- ✅ http://localhost:5280/Users/Index ← **MUST WORK**
- ✅ http://localhost:5280/Account/Login

---

## 🎯 NẾU VẪN 404 SAU KHI RESTART

Có thể là do session chưa được set. Thử:

1. Đăng xuất: http://localhost:5280/Account/Logout
2. Đăng nhập lại với admin credentials
3. Test lại các routes

---

## 🔒 VẤN ĐỀ AUTHORIZATION

Nếu redirect về /Account/Login thay vì 404:
- ✅ Đây là behavior đúng! (do BaseAdminController)
- Đăng nhập với admin credentials
- Sau đó test lại

---

## 📞 HÃY CHO TÔI BIẾT:

1. Console output khi chạy `dotnet run`
2. Browser console errors (F12)
3. Network tab response cho `/Users/Index` và `/Attendance/Index`

Tôi sẽ fix tiếp dựa trên thông tin đó!
