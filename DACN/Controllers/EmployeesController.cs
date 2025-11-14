
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using System.IO;
using System;
using System.Linq;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;
using Data;
using Models;
using BCrypt.Net;

namespace Controllers
{
    public class EmployeesController : BaseAdminController
    {
        private readonly AppDbContext _context;
        private readonly ILogger<EmployeesController> _logger;
        private readonly IConfiguration _configuration;
        
        public EmployeesController(AppDbContext context, ILogger<EmployeesController> logger, IConfiguration configuration)
        {
            _context = context;
            _logger = logger;
            _configuration = configuration;
        }

        [HttpGet]
        public IActionResult Index()
        {            var employees = _context.Employees.ToList();
            return View(employees);
        }

        // Action GET để hiển thị form thêm mới
        [HttpGet]
        public IActionResult Create()
        {            // Khởi tạo Model mặc định để tránh lỗi null
            var emp = new Models.Employee();
            return View(emp);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Create(Employee emp, IFormFile FaceImage)
        {            try
            {
                // Luôn đặt Role = "employee" ngay từ đầu
                emp.Role = "employee";
                
                // Kiểm tra Phone/Username đã tồn tại chưa
                if (!string.IsNullOrEmpty(emp.Phone) && _context.Users.Any(u => u.Username == emp.Phone))
                {
                    ViewBag.ErrorMessage = "Số điện thoại này đã được dùng làm tài khoản.";
                    return View(emp);
                }

                if (ModelState.IsValid)
                {
                    
                    if (FaceImage != null && FaceImage.Length > 0)
                    {
                        var uploads = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot/photos");
                        if (!Directory.Exists(uploads)) Directory.CreateDirectory(uploads);
                        var fileName = $"emp_{DateTime.Now.Ticks}_{Path.GetFileName(FaceImage.FileName)}";
                        var filePath = Path.Combine(uploads, fileName);

                        using (var stream = new FileStream(filePath, FileMode.Create))
                        {
                            FaceImage.CopyTo(stream);
                        }
                        emp.PhotoPath = "/photos/" + fileName;

                        // Tự động gửi ảnh tới API Backend để lấy face embedding
                        try
                        {
                            // Đảm bảo Backend API đang chạy tại http://localhost:8000
                            using (var httpClient = new System.Net.Http.HttpClient())
                            {
                                // Set timeout để không chờ quá lâu nếu API không chạy
                                httpClient.Timeout = TimeSpan.FromSeconds(10);
                                
                                using (var form = new System.Net.Http.MultipartFormDataContent())
                                {
                                    var imgBytes = System.IO.File.ReadAllBytes(filePath);
                                    var imgContent = new System.Net.Http.ByteArrayContent(imgBytes);
                                    imgContent.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg"); 
                                    form.Add(imgContent, "image", fileName);
                                    form.Add(new System.Net.Http.StringContent(emp.Name ?? "Unknown"), "name");
                                    
                                    var response = httpClient.PostAsync("http://localhost:8000/api/faceid/add_face", form).Result; 
                                    
                                    if (response.IsSuccessStatusCode)
                                    {
                                        var json = response.Content.ReadAsStringAsync().Result;
                                        var embedding = ExtractEmbeddingFromApiResponse(json);
                                        if (embedding != null)
                                        {
                                            emp.FaceEmbedding = embedding;
                                            _logger?.LogInformation($"Successfully extracted face embedding for {emp.Name}");
                                        }
                                        else
                                        {
                                            _logger?.LogWarning($"API returned success but no embedding found for {emp.Name}");
                                            TempData["WarningMessage"] = "⚠️ Thêm nhân viên thành công, nhưng không nhận diện được khuôn mặt. Vui lòng upload ảnh rõ mặt hơn.";
                                        }
                                    }
                                    else
                                    {
                                        var errorContent = response.Content.ReadAsStringAsync().Result;
                                        _logger?.LogWarning($"API returned error: {response.StatusCode} - {errorContent}");
                                        TempData["WarningMessage"] = $"⚠️ Không thể xử lý ảnh khuôn mặt: {response.ReasonPhrase}. Nhân viên vẫn được tạo.";
                                    }
                                }
                            }
                        }
                        catch (System.Net.Http.HttpRequestException ex)
                        {
                            _logger?.LogWarning($"Cannot connect to Backend API: {ex.Message}");
                            TempData["WarningMessage"] = "⚠️ Không thể kết nối Backend API (port 8000). Nhân viên được tạo nhưng chưa có Face ID. Hãy chạy Backend API và thử lại.";
                        }
                        catch (TaskCanceledException ex)
                        {
                            _logger?.LogWarning($"Backend API timeout: {ex.Message}");
                            TempData["WarningMessage"] = "⚠️ Backend API phản hồi quá chậm. Nhân viên được tạo nhưng chưa có Face ID.";
                        }
                        catch (Exception ex)
                        {
                            _logger?.LogWarning($"Failed to get face embedding: {ex.Message}");
                            TempData["WarningMessage"] = "⚠️ Lỗi xử lý ảnh khuôn mặt. Nhân viên vẫn được tạo nhưng cần upload lại ảnh.";
                        }
                    }
                    
                    _context.Employees.Add(emp);
                    _context.SaveChanges();

                    // Tạo tài khoản user cho nhân viên nếu chưa tồn tại
                    if (!string.IsNullOrEmpty(emp.Phone))
                    {
                        var username = emp.Phone;
                        var password = "123456";
                        var passwordHash = BCrypt.Net.BCrypt.HashPassword(password);
                        
                        // Kiểm tra lại sau khi SaveChanges() cho Employees để đảm bảo ID đã được tạo
                        var existedUser = _context.Users.FirstOrDefault(u => u.Username == username);
                        if (existedUser == null)
                        {
                            var user = new User
                            {
                                Username = username,
                                PasswordHash = passwordHash,
                                Role = "Employee",
                                EmployeeId = emp.Id // emp.Id đã có giá trị sau SaveChanges() đầu tiên
                            };
                            _context.Users.Add(user);
                            _context.SaveChanges();
                            
                            // Gửi email chỉ khi tạo tài khoản thành công
                            SendEmail(emp.Email ?? "", emp.Name ?? "", emp.Phone ?? "");
                        }
                    }
                    
                    // Chỉ hiển thị Success nếu KHÔNG có Warning
                    if (TempData["WarningMessage"] == null)
                    {
                        TempData["SuccessMessage"] = "✅ Thêm nhân viên thành công, đã gửi email thông báo!";
                    }
                    
                    return RedirectToAction("Index");
                }

                var errors = string.Join("; ", ModelState.Values.SelectMany(v => v.Errors).Select(e => e.ErrorMessage));
                ViewBag.ErrorMessage = $"Thêm nhân viên thất bại. Lỗi: {errors}";
                return View(emp);
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error creating employee");
                ViewBag.ErrorMessage = "Thêm nhân viên thất bại: " + ex.Message;
                return View(emp);
            }
        }

        // Hàm hỗ trợ giải mã embedding từ API Flask (giả sử trả về base64)
        private byte[]? ExtractEmbeddingFromApiResponse(string json)
        {
            try
            {
                // Sử dụng System.Text.Json.JsonDocument để parse (cần using System.Text.Json;)
                var obj = JsonDocument.Parse(json);
                // API trả về "embedding_b64" chứ không phải "embedding"
                if (obj.RootElement.TryGetProperty("embedding_b64", out var emb))
                {
                    var base64 = emb.GetString();
                    if (!string.IsNullOrEmpty(base64))
                        return Convert.FromBase64String(base64);
                }
            }
            catch { }
            return null;
        }

        // Hàm gửi email đơn giản
        private void SendEmail(string toEmail, string empName, string phone)
        {
            try
            {
                // Đọc cấu hình SMTP từ appsettings.json
                var config = _configuration.GetSection("EmailSettings");
                var smtpHost = config["SmtpHost"];
                var smtpPort = int.Parse(config["SmtpPort"] ?? "587");
                var enableSsl = bool.Parse(config["EnableSsl"] ?? "true");
                var fromEmail = config["FromEmail"] ?? "your_email@gmail.com";
                var fromName = config["FromName"] ?? "Admin";
                var username = config["Username"] ?? fromEmail;
                var password = config["Password"] ?? "";

                // Kiểm tra xem email có được cấu hình chưa
                if (string.IsNullOrEmpty(smtpHost) || string.IsNullOrEmpty(password) || password == "your_app_password_here")
                {
                    _logger.LogWarning("Email chưa được cấu hình. Vui lòng cập nhật EmailSettings trong appsettings.json");
                    return;
                }

                var fromAddress = new System.Net.Mail.MailAddress(fromEmail, fromName);
                var toAddress = new System.Net.Mail.MailAddress(toEmail, empName);
                string subject = "🎉 Chào mừng bạn đến với Hệ Thống Chấm Công DACN";
                
                // Email body với HTML format chuyên nghiệp
                string body = $@"
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa; }}
        .card {{ background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ width: 80px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; }}
        .logo-text {{ color: white; font-size: 36px; font-weight: bold; }}
        h1 {{ color: #2c3e50; margin: 0; font-size: 24px; }}
        .welcome {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
        .info-box {{ background: #f1f3f5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
        .credential {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e9ecef; }}
        .credential:last-child {{ border-bottom: none; }}
        .label {{ font-weight: 600; color: #495057; }}
        .value {{ color: #6c757d; font-family: 'Courier New', monospace; background: #fff; padding: 4px 12px; border-radius: 4px; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #e9ecef; color: #6c757d; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: 600; }}
    </style>
</head>
<body>
    <div class='container'>
        <div class='card'>
            <div class='header'>
                <div class='logo'>
                    <span class='logo-text'>👤</span>
                </div>
                <h1>Hệ thống Chấm công DACN</h1>
            </div>
            
            <div class='welcome'>
                <h2 style='margin: 0; font-size: 20px;'>🎉 Chào mừng {empName}!</h2>
                <p style='margin: 10px 0 0 0;'>Bạn đã được thêm vào hệ thống chấm công</p>
            </div>
            
            <p>Xin chào <strong>{empName}</strong>,</p>
            <p>Chúc mừng bạn! Tài khoản của bạn đã được tạo thành công trong <strong>Hệ thống Chấm công DACN</strong>.</p>
            
            <div class='info-box'>
                <h3 style='margin-top: 0; color: #495057;'>📋 Thông tin đăng nhập</h3>
                <div class='credential'>
                    <span class='label'>Tài khoản:</span>
                    <span class='value'>{phone}</span>
                </div>
                <div class='credential'>
                    <span class='label'>Mật khẩu:</span>
                    <span class='value'>123456</span>
                </div>
            </div>
            
            <div class='warning'>
                <strong>⚠️ Lưu ý quan trọng:</strong>
                <ul style='margin: 10px 0 0 0; padding-left: 20px;'>
                    <li>Đây là mật khẩu tạm thời</li>
                    <li>Vui lòng <strong>đổi mật khẩu</strong> ngay sau lần đăng nhập đầu tiên</li>
                    <li>Không chia sẻ thông tin đăng nhập với người khác</li>
                </ul>
            </div>
            
            <p style='text-align: center;'>
                <a href='http://localhost:5280' class='btn'>🚀 Đăng nhập ngay</a>
            </p>
            
            <div class='footer'>
                <p><strong>Hệ thống Chấm công DACN</strong></p>
                <p>Email: {fromEmail} | Hỗ trợ: 24/7</p>
                <p style='font-size: 12px; color: #adb5bd;'>© 2025 DACN System. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>";

                var smtp = new System.Net.Mail.SmtpClient
                {
                    Host = smtpHost,
                    Port = smtpPort,
                    EnableSsl = enableSsl,
                    DeliveryMethod = System.Net.Mail.SmtpDeliveryMethod.Network,
                    UseDefaultCredentials = false,
                    Credentials = new System.Net.NetworkCredential(username, password)
                };
                using (var message = new System.Net.Mail.MailMessage(fromAddress, toAddress)
                {
                    Subject = subject,
                    Body = body,
                    IsBodyHtml = true  // Quan trọng: Enable HTML
                })
                {
                    smtp.Send(message);
                    _logger.LogInformation($"Email sent successfully to {toEmail}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Failed to send email to {toEmail}");
            }
        }

        [HttpGet]
        public IActionResult Edit(int id)
        {            var emp = _context.Employees.Find(id);
            if (emp == null) return NotFound();
            return View(emp);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Edit(Employee emp, IFormFile FaceImage) // Thêm IFormFile để xử lý ảnh khi chỉnh sửa
        {            // Lấy thông tin nhân viên cũ trước khi cập nhật
            var dbEmp = _context.Employees.AsNoTracking().FirstOrDefault(e => e.Id == emp.Id);

            if (ModelState.IsValid && dbEmp != null)
            {
                // Xử lý ảnh mới và face embedding nếu có
                if (FaceImage != null && FaceImage.Length > 0)
                {
                    var uploads = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot/photos");
                    if (!Directory.Exists(uploads)) Directory.CreateDirectory(uploads);
                    var fileName = $"emp_{DateTime.Now.Ticks}_{Path.GetFileName(FaceImage.FileName)}";
                    var filePath = Path.Combine(uploads, fileName);

                    using (var stream = new FileStream(filePath, FileMode.Create))
                    {
                        FaceImage.CopyTo(stream);
                    }
                    emp.PhotoPath = "/photos/" + fileName;

                    // Gửi ảnh tới API Flask để lấy face embedding mới
                    try
                    {
                        using (var httpClient = new System.Net.Http.HttpClient())
                        using (var form = new System.Net.Http.MultipartFormDataContent())
                        {
                            var imgBytes = System.IO.File.ReadAllBytes(filePath);
                            var imgContent = new System.Net.Http.ByteArrayContent(imgBytes);
                            imgContent.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg");
                            form.Add(imgContent, "image", fileName);
                            form.Add(new System.Net.Http.StringContent(emp.Name ?? "Unknown"), "name");
                            var response = httpClient.PostAsync("http://localhost:5000/add_face", form).Result;
                            
                            if (response.IsSuccessStatusCode)
                            {
                                var json = response.Content.ReadAsStringAsync().Result;
                                var embedding = ExtractEmbeddingFromApiResponse(json);
                                if (embedding != null)
                                    emp.FaceEmbedding = embedding;
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex, "Failed to update face embedding");
                        TempData["WarningMessage"] = "Cập nhật nhân viên thành công, nhưng **cập nhật Face Embedding thất bại**. Kiểm tra API Server.";
                        // Nếu thất bại, giữ lại embedding cũ
                        emp.FaceEmbedding = dbEmp.FaceEmbedding; 
                    }
                }
                else
                {
                    // Nếu không có ảnh mới, giữ lại đường dẫn ảnh và embedding cũ
                    emp.PhotoPath = dbEmp.PhotoPath;
                    emp.FaceEmbedding = dbEmp.FaceEmbedding;
                }
                
                // Cập nhật thông tin nhân viên
                _context.Employees.Update(emp);
                _context.SaveChanges();
                
                // Cập nhật User Role (nếu cần)
                var userAccount = _context.Users.FirstOrDefault(u => u.EmployeeId == emp.Id);
                if (userAccount != null)
                {
                    // Giả sử Role trong User được đồng bộ với Role trong Employee
                    // dbEmp.Role đã được cập nhật ở dòng 415
                    // Nếu cần lưu Role trong bảng User, bạn có thể thêm logic ở đây
                    // userAccount.Role = emp.Role; 
                    // _context.Users.Update(userAccount);
                    // _context.SaveChanges();
                }

                TempData["SuccessMessage"] = TempData["WarningMessage"] != null ? 
                    TempData["WarningMessage"] : "Cập nhật nhân viên thành công!";

                return RedirectToAction("Index");
            }
            
            ViewBag.ErrorMessage = "Cập nhật nhân viên thất bại. Vui lòng kiểm tra lại thông tin.";
            return View(emp);
        }

        public IActionResult Delete(int id)
        {            var emp = _context.Employees.Find(id);
            if (emp == null) return NotFound();
            return View(emp);
        }

        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public IActionResult DeleteConfirmed(int id)
        {            var emp = _context.Employees.Find(id);
            if (emp != null)
            {
                // Xóa tài khoản người dùng liên quan
                var userAccount = _context.Users.FirstOrDefault(u => u.EmployeeId == id);
                if (userAccount != null)
                {
                    _context.Users.Remove(userAccount);
                }
                
                _context.Employees.Remove(emp);
                _context.SaveChanges();
                TempData["SuccessMessage"] = "Xóa nhân viên thành công!";
            }
            return RedirectToAction("Index");
        }

        public IActionResult Lock(int id)
        {            var emp = _context.Employees.Find(id);
            if (emp != null)
            {
                emp.IsLocked = true;
                _context.Employees.Update(emp);
                _context.SaveChanges();
                TempData["SuccessMessage"] = $"Đã khóa nhân viên **{emp.Name}**.";
            }
            return RedirectToAction("Index");
        }

        public IActionResult Unlock(int id)
        {            var emp = _context.Employees.Find(id);
            if (emp != null)
            {
                emp.IsLocked = false;
                _context.Employees.Update(emp);
                _context.SaveChanges();
                TempData["SuccessMessage"] = $"Đã mở khóa nhân viên **{emp.Name}**.";
            }
            return RedirectToAction("Index");
        }
    }
}