
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore; // <-- Thêm để dùng AsNoTracking
using System.IO;
using System;
using System.Linq;
using System.Net.Http.Headers; // <-- Đã thêm
using System.Text.Json; // <-- Đã thêm để hỗ trợ JsonDocument
using Data;
using Models;
using BCrypt.Net;

namespace DACN.Controllers
{
    public class EmployeesController : Controller
    {
        private readonly AppDbContext _context;
        public EmployeesController(AppDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public IActionResult Index()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var employees = _context.Employees.ToList();
            return View(employees);
        }

        // Action GET để hiển thị form thêm mới
        [HttpGet]
        public IActionResult Create()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            // Khởi tạo Model mặc định để tránh lỗi null
            var emp = new Models.Employee();
            return View(emp);
        }

        [HttpPost]
        [ValidateAntiForgeryToken] // Nên có để bảo mật
        public IActionResult Create(Employee emp, IFormFile FaceImage)
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            try
            {
                // Kiểm tra Phone/Username đã tồn tại chưa
                if (!string.IsNullOrEmpty(emp.Phone) && _context.Users.Any(u => u.Username == emp.Phone))
                {
                    ModelState.AddModelError("Phone", "Số điện thoại này đã được dùng làm tài khoản.");
                }

                if (ModelState.IsValid)
                {
                    emp.Role = "employee";
                    
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

                        // Tự động gửi ảnh tới API Flask để lấy face embedding
                        try
                        {
                            // Đảm bảo API Flask đang chạy tại http://localhost:5000/add_face
                            using (var httpClient = new System.Net.Http.HttpClient())
                            using (var form = new System.Net.Http.MultipartFormDataContent())
                            {
                                var imgBytes = System.IO.File.ReadAllBytes(filePath);
                                var imgContent = new System.Net.Http.ByteArrayContent(imgBytes);
                                // Sửa lỗi tiềm ẩn: Thay vì dùng System.Net.Http.Headers.MediaTypeHeaderValue("image/jpeg") 
                                // vì đã thêm using System.Net.Http.Headers; ở trên
                                imgContent.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg"); 
                                form.Add(imgContent, "image", fileName);
                                form.Add(new System.Net.Http.StringContent(emp.Name ?? "Unknown"), "name");
                                
                                // Đổi .Result thành await để tránh deadlock (nên dùng async/await)
                                // Hiện tại giữ nguyên .Result vì Controller action chưa là async
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
                            // Cảnh báo nếu không lấy được embedding nhưng vẫn tạo nhân viên
                            System.Diagnostics.Debug.WriteLine($"[EMBEDDING ERROR] {ex.Message}");
                            TempData["WarningMessage"] = "Thêm nhân viên thành công, nhưng **lấy Face Embedding thất bại**. Kiểm tra API Server.";
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
                                EmployeeId = emp.Id // emp.Id đã có giá trị sau SaveChanges() đầu tiên
                            };
                            _context.Users.Add(user);
                            _context.SaveChanges();
                            
                            // Gửi email chỉ khi tạo tài khoản thành công
                            SendEmail(emp.Email ?? "", emp.Name ?? "", emp.Phone ?? "");
                        }
                    }
                    
                    TempData["SuccessMessage"] = TempData["WarningMessage"] != null ? 
                        TempData["WarningMessage"] : "Thêm nhân viên thành công và đã gửi email!";
                    return RedirectToAction("Index");
                }

                ViewBag.ErrorMessage = "Thêm nhân viên thất bại. Vui lòng kiểm tra lại thông tin.";
                return View(emp);
            }
            catch (Exception ex)
            {
                string errorMsg = ex.Message;
                if (ex.InnerException != null)
                {
                    errorMsg += " | Inner: " + ex.InnerException.Message;
                }
                System.Diagnostics.Debug.WriteLine($"[CREATE ERROR] {errorMsg}");
                ViewBag.ErrorMessage = "Thêm nhân viên thất bại: " + errorMsg;
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
                if (obj.RootElement.TryGetProperty("embedding", out var emb))
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
                    System.Diagnostics.Debug.WriteLine($"[EMAIL SUCCESS] Sent to {toEmail}");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[EMAIL ERROR] To: {toEmail}, Name: {empName}, Phone: {phone}, Error: {ex.Message}");
            }
        }

        [HttpGet]
        public IActionResult Edit(int id)
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var emp = _context.Employees.Find(id);
            if (emp == null) return NotFound();
            return View(emp);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Edit(Employee emp, IFormFile FaceImage) // Thêm IFormFile để xử lý ảnh khi chỉnh sửa
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            
            // Lấy thông tin nhân viên cũ trước khi cập nhật
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
                        System.Diagnostics.Debug.WriteLine($"[EMBEDDING UPDATE ERROR] {ex.Message}");
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
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var emp = _context.Employees.Find(id);
            if (emp == null) return NotFound();
            return View(emp);
        }

        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public IActionResult DeleteConfirmed(int id)
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var emp = _context.Employees.Find(id);
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
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var emp = _context.Employees.Find(id);
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
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var emp = _context.Employees.Find(id);
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