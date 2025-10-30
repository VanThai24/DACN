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
                HttpContext.Session.SetString("User", user.Username);
                return Redirect("http://localhost:5280/Admin/Dashboard");
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
