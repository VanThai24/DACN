using Twilio;
using Twilio.Rest.Api.V2010.Account;
using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;

namespace Controllers
{
    public class EmployeesController : Controller
    {
        private readonly AppDbContext _context;
        public EmployeesController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var employees = _context.Employees.ToList();
            return View(employees);
        }

        public IActionResult Details(int id)
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var emp = _context.Employees.Find(id);
            if (emp == null) return NotFound();
            return View(emp);
        }

        public IActionResult Create()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            return View(new Employee());
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
                    // Gán cứng role là 'employee' khi tạo mới
                    emp.Role = "employee";
                    System.Diagnostics.Debug.WriteLine($"[DEBUG] emp.Role = '{emp.Role}'");
                    // Xử lý lưu file ảnh nếu có
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
                    }
                    _context.Employees.Add(emp);
                    _context.SaveChanges();

                    // Tạo tài khoản user cho nhân viên nếu chưa tồn tại
                    if (!string.IsNullOrEmpty(emp.Phone))
                    {
                        var username = emp.Phone;
                        var password = "123456";
                        var passwordHash = BCrypt.Net.BCrypt.HashPassword(password);
                        // Kiểm tra user đã tồn tại chưa
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

                            // Gửi SMS thông báo tài khoản cho nhân viên
                            try
                            {
                                // Thay các giá trị này bằng thông tin Twilio thật của bạn
                                var accountSid = "YOUR_TWILIO_ACCOUNT_SID";
                                var authToken = "YOUR_TWILIO_AUTH_TOKEN";
                                var fromPhone = "+1234567890"; // Số điện thoại Twilio
                                TwilioClient.Init(accountSid, authToken);
                                var messageBody = $"Chúc mừng bạn đã được thêm vào hệ thống!\nTài khoản: {username}\nMật khẩu: {password}\nVui lòng đăng nhập và đổi mật khẩu.";
                                var message = MessageResource.Create(
                                    body: messageBody,
                                    from: new Twilio.Types.PhoneNumber(fromPhone),
                                    to: new Twilio.Types.PhoneNumber(emp.Phone)
                                );
                            }
                            catch (Exception ex)
                            {
                                System.Diagnostics.Debug.WriteLine($"[SMS ERROR] {ex.Message}");
                            }
                        }
                    }
                    TempData["SuccessMessage"] = "Thêm nhân viên thành công!";
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
                _context.Employees.Update(emp);
                _context.SaveChanges();
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
    }
}
