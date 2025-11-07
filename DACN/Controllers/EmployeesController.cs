using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Http;
using System.IO;
using System;
using System.Linq;
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

        [HttpPost]
        public IActionResult Create(Employee emp, IFormFile FaceImage)
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            try
            {
                if (ModelState.IsValid)
                {
                    emp.Role = "employee";
                    System.Diagnostics.Debug.WriteLine($"[DEBUG] emp.Role = '{emp.Role}'");
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
                            using (var httpClient = new System.Net.Http.HttpClient())
                            using (var form = new System.Net.Http.MultipartFormDataContent())
                            {
                                var imgBytes = System.IO.File.ReadAllBytes(filePath);
                                var imgContent = new System.Net.Http.ByteArrayContent(imgBytes);
                                imgContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("image/jpeg");
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
                            System.Diagnostics.Debug.WriteLine($"[EMBEDDING ERROR] {ex.Message}");
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
                        var existedUser = _context.Users.FirstOrDefault(u => u.Username == username);
                        if (existedUser == null)
                        {
                            var user = new User
                            {
                                Username = username,
                                PasswordHash = passwordHash,
                                EmployeeId = emp.Id
                            };
                            _context.Users.Add(user);
                            _context.SaveChanges();
                        }
                    }
                    // Gửi email thông báo tài khoản cho nhân viên
                    SendEmail(emp.Email ?? "", emp.Name ?? "", emp.Phone ?? "");
                    TempData["SuccessMessage"] = "Thêm nhân viên thành công và đã gửi email!";
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
                // Sử dụng Newtonsoft.Json hoặc System.Text.Json để parse
                var obj = System.Text.Json.JsonDocument.Parse(json);
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
                        const string fromPassword = "your_email_password"; // Thay bằng mật khẩu thật hoặc dùng app password
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
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"[EMAIL ERROR] {ex.Message}");
                    }
                }

                // Không cần hàm hash SHA256 nữa, đã dùng BCrypt.Net để hash password

                public IActionResult Edit(int id)
                {
                    if (HttpContext.Session.GetString("User") == null)
                        return Redirect("/Account/Login");
                    var emp = _context.Employees.Find(id);
                    if (emp == null) return NotFound();
                    return View(emp);
                }

                [HttpPost]
                public IActionResult Edit(Employee emp)
                {
                    if (HttpContext.Session.GetString("User") == null)
                        return Redirect("/Account/Login");
                    if (ModelState.IsValid)
                    {
                        var dbEmp = _context.Employees.Find(emp.Id);
                        if (dbEmp != null)
                        {
                            dbEmp.Name = emp.Name;
                            dbEmp.Department = emp.Department;
                            dbEmp.Role = emp.Role;
                            dbEmp.Email = emp.Email;
                            dbEmp.Phone = emp.Phone;
                            dbEmp.FaceEmbedding = emp.FaceEmbedding;
                            dbEmp.IsLocked = emp.IsLocked;
                            _context.Employees.Update(dbEmp);
                            _context.SaveChanges();
                        }
                        return RedirectToAction("Index");
                    }
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
                public IActionResult DeleteConfirmed(int id)
                {
                    if (HttpContext.Session.GetString("User") == null)
                        return Redirect("/Account/Login");
                    var emp = _context.Employees.Find(id);
                    if (emp != null)
                    {
                        _context.Employees.Remove(emp);
                        _context.SaveChanges();
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
                    }
                    return RedirectToAction("Index");
                }
        // ...existing code...
    }
}
