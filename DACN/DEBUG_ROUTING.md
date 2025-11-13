## DEBUG ROUTING ISSUE

### Test URLs trong browser (sau khi đăng nhập):

1. ✅ http://localhost:5280/Admin/Dashboard - Works
2. ✅ http://localhost:5280/Employees/Index - Works  
3. ❌ http://localhost:5280/Users/Index - 404
4. ❌ http://localhost:5280/Users - 404

### Kiểm tra trong VS Code Terminal:

```powershell
# Test với curl (trong PowerShell mới, không dùng terminal đang chạy app)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$cookie = New-Object System.Net.Cookie
$cookie.Name = ".AspNetCore.Session"
$cookie.Value = "your_session_cookie_here"
$cookie.Domain = "localhost"
$session.Cookies.Add($cookie)

Invoke-WebRequest -Uri "http://localhost:5280/Users/Index" -WebSession $session -UseBasicParsing
```

### VẤN ĐỀ CÓ THỂ:

1. **Browser cache 404 page**
   - Clear cache: Ctrl + Shift + Delete
   - Hard refresh: Ctrl + F5
   - Hoặc dùng Incognito mode

2. **Route không match do case sensitivity**
   - ASP.NET Core default là case-insensitive
   - Nhưng có thể bị override

3. **Controller không được discover**
   - Kiểm tra namespace: `Controllers`
   - Kiểm tra class name: `UsersController`
   - Kiểm tra inheritance: `: BaseAdminController`

4. **View không được tìm thấy**
   - Path phải là: `Views/Users/Index.cshtml`
   - Hoặc: `Views/Shared/Index.cshtml`

### GIẢI PHÁP:

#### Option 1: Add explicit route attribute

Thêm vào UsersController:

```csharp
[Route("Users")]
public class UsersController : BaseAdminController
{
    [Route("")]
    [Route("Index")]
    public IActionResult Index()
    {
        var users = _context.Users.ToList();
        return View(users);
    }
}
```

#### Option 2: Test với URL lowercase

Thử: `http://localhost:5280/users/index` (all lowercase)

#### Option 3: Check routing in Startup

Verify Program.cs có:
```csharp
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Admin}/{action=Dashboard}/{id?}")
```

### DEBUG STEPS:

1. Mở browser Console (F12)
2. Truy cập /Users/Index
3. Check Network tab:
   - Status code?
   - Response headers?
   - Request URL?

4. Check terminal output:
   - Có log request đến /Users không?
   - Có error message không?

5. Test endpoints khác:
   - /Attendance/Index - Works?
   - /Devices/Index - Works?
   - /Shifts/Index - Works?

Nếu các controller khác work mà chỉ /Users không work → vấn đề ở UsersController specific

Nếu tất cả routes có pattern /{Controller}/Index đều 404 → vấn đề ở routing configuration
