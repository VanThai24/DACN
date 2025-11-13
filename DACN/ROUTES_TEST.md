# Test all routes in AdminWeb

## Expected Routes (All should return 200 or redirect to Login if not authenticated)

### Admin Routes
- GET /Admin/Dashboard
- GET /Admin/Reports
- GET /Admin/Faces
- GET /Admin/CreateReport (form)
- POST /Admin/CreateReport
- GET /Admin/DownloadReport/{id}
- POST /Admin/DeleteReport/{id}

### Employees Routes
- GET /Employees/Index
- GET /Employees/Create
- POST /Employees/Create
- GET /Employees/Edit/{id}
- POST /Employees/Edit/{id}
- GET /Employees/Delete/{id}
- POST /Employees/Delete/{id}
- GET /Employees/Details/{id}

### Devices Routes
- GET /Devices/Index
- GET /Devices/Create
- POST /Devices/Create
- GET /Devices/Edit/{id}
- POST /Devices/Edit/{id}
- GET /Devices/Delete/{id}
- POST /Devices/Delete/{id}
- GET /Devices/Details/{id}

### Attendance Routes
- GET /Attendance/Index
- GET /Attendance/Create
- POST /Attendance/Create
- GET /Attendance/Edit/{id}
- POST /Attendance/Edit/{id}
- GET /Attendance/Delete/{id}
- POST /Attendance/Delete/{id}
- GET /Attendance/Details/{id}

### Shifts Routes
- GET /Shifts/Index
- GET /Shifts/Create
- POST /Shifts/Create
- GET /Shifts/Edit/{id}
- POST /Shifts/Edit/{id}
- GET /Shifts/Delete/{id}
- POST /Shifts/Delete/{id}
- GET /Shifts/Details/{id}

### Users Routes (NEW - FIXED)
- GET /Users/Index ✅
- GET /Users/Create ✅
- POST /Users/Create ✅
- GET /Users/Edit/{id} ✅
- POST /Users/Edit/{id} ✅
- GET /Users/Delete/{id} ✅
- POST /Users/Delete/{id} ✅
- GET /Users/Details/{id} ✅
- GET /Users/ChangePassword/{id} ✅
- POST /Users/ChangePassword/{id} ✅

### Account Routes
- GET /Account/Login
- POST /Account/Login
- GET /Account/Logout

---

## Route Configuration

**Program.cs:**
```csharp
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Admin}/{action=Dashboard}/{id?}")
    .WithStaticAssets();
```

This single route handles ALL controllers:
- /Admin/Dashboard → AdminController.Dashboard()
- /Employees/Index → EmployeesController.Index()
- /Devices/Index → DevicesController.Index()
- /Attendance/Index → AttendanceController.Index()
- /Shifts/Index → ShiftsController.Index()
- /Users/Index → UsersController.Index() ✅ FIXED
- /Account/Login → AccountController.Login()

---

## Fixed Issues

1. ✅ Added default route that covers all controllers
2. ✅ Removed redundant specific routes
3. ✅ Fixed navbar links to use consistent format
4. ✅ Removed duplicate "Quản lý khuôn mặt" menu item
5. ✅ All controllers now accessible via /{Controller}/{Action}/{id?}

---

## Testing Checklist

After starting the application with `dotnet run`:

1. [ ] Navigate to http://localhost:5280/
2. [ ] Should redirect to /Admin/Dashboard (or /Account/Login if not logged in)
3. [ ] Login with admin credentials
4. [ ] Test all navbar links:
   - [ ] Dashboard
   - [ ] Nhân viên (Employees)
   - [ ] Báo cáo (Reports)
   - [ ] Thiết bị (Devices)
   - [ ] Điểm danh (Attendance)
   - [ ] Ca làm (Shifts)
   - [ ] Quản lý khuôn mặt (Faces)
   - [ ] Người dùng (Users) ✅
5. [ ] Test CRUD operations for each entity
6. [ ] Verify all pages load without 404 errors
7. [ ] Check that non-Admin users are blocked

---

## Status: READY TO TEST 🚀
