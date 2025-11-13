using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;
using Microsoft.AspNetCore.Http;

namespace Controllers
{
    public class AccountController : Controller
    {
        private readonly AppDbContext _context;
        public AccountController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Login()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Login(string username, string password)
        {
            var user = _context.Users.FirstOrDefault(u => u.Username == username);
            if (user != null && BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
            {
                // Chỉ cho phép Admin và Manager đăng nhập
                if (user.Role != "Admin" && user.Role != "Manager")
                {
                    ViewBag.Error = "Bạn không có quyền truy cập hệ thống Admin!";
                    return View();
                }

                HttpContext.Session.SetString("User", user.Username ?? "");
                HttpContext.Session.SetString("UserRole", user.Role ?? "User");
                HttpContext.Session.SetInt32("UserId", user.Id);
                return Redirect("/Admin/Dashboard");
            }
            ViewBag.Error = "Sai tài khoản hoặc mật khẩu";
            return View();
        }

        public IActionResult Logout()
        {
            HttpContext.Session.Remove("User");
            return RedirectToAction("Login");
        }
    }
}
