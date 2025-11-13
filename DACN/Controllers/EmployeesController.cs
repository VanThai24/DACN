
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
        
        public EmployeesController(AppDbContext context, ILogger<EmployeesController> logger)
        {
            _context = context;
            _logger = logger;
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
                var fromAddress = new System.Net.Mail.MailAddress("your_email@gmail.com", "Admin");
                var toAddress = new System.Net.Mail.MailAddress(toEmail, empName);
                // CHÚ Ý: Thay bằng mật khẩu thật hoặc dùng App Password của Gmail nếu dùng Gmail
                const string fromPassword = "your_email_password"; 
                string subject = "Thông báo thêm nhân viên";
                string body = $"Chào {empName}, bạn đã được thêm vào hệ thống. Tài khoản đăng nhập: {phone}, mật khẩu mặc định: 123456. Vui lòng đăng nhập và đổi mật khẩu.";

                var smtp = new System.Net.Mail.SmtpClient
                {
                    Host = "smtp.gmail.com",
                    Port = 587,
                    EnableSsl = true,
                    DeliveryMethod = System.Net.Mail.SmtpDeliveryMethod.Network,
                    UseDefaultCredentials = false,
                    Credentials = new System.Net.NetworkCredential(fromAddress.Address, fromPassword)
                };
                using (var message = new System.Net.Mail.MailMessage(fromAddress, toAddress)
                {
                    Subject = subject,
                    Body = body
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