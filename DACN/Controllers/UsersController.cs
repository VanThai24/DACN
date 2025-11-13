using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;

namespace Controllers
{
    [Route("Users")]
    public class UsersController : BaseAdminController
    {
        private readonly AppDbContext _context;
        public UsersController(AppDbContext context)
        {
            _context = context;
        }

        // GET: Users
        [Route("")]
        [Route("Index")]
        public IActionResult Index()
        {
            var users = _context.Users.ToList();
            return View(users);
        }

        // GET: Users/Details/5
        [Route("Details/{id}")]
        public IActionResult Details(int id)
        {
            var user = _context.Users.Find(id);
            if (user == null) return NotFound();
            return View(user);
        }

        // GET: Users/Create
        [Route("Create")]
        public IActionResult Create()
        {
            return View();
        }

        // POST: Users/Create
        [HttpPost]
        [Route("Create")]
        [ValidateAntiForgeryToken]
        public IActionResult Create(User user)
        {
            if (ModelState.IsValid)
            {
                // Hash password với BCrypt
                user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(user.PasswordHash);
                _context.Users.Add(user);
                _context.SaveChanges();
                TempData["Success"] = "Người dùng đã được tạo thành công!";
                return RedirectToAction(nameof(Index));
            }
            return View(user);
        }

        // GET: Users/Edit/5
        [Route("Edit/{id}")]
        public IActionResult Edit(int id)
        {
            var user = _context.Users.Find(id);
            if (user == null) return NotFound();
            return View(user);
        }

        // POST: Users/Edit/5
        [HttpPost]
        [Route("Edit/{id}")]
        [ValidateAntiForgeryToken]
        public IActionResult Edit(int id, User user, string? newPassword)
        {
            if (id != user.Id) return NotFound();
            
            if (ModelState.IsValid)
            {
                var existingUser = _context.Users.Find(id);
                if (existingUser != null)
                {
                    existingUser.Username = user.Username;
                    existingUser.Role = user.Role;
                    
                    // Chỉ cập nhật mật khẩu nếu có nhập mật khẩu mới
                    if (!string.IsNullOrEmpty(newPassword))
                    {
                        existingUser.PasswordHash = BCrypt.Net.BCrypt.HashPassword(newPassword);
                    }
                    
                    _context.Update(existingUser);
                    _context.SaveChanges();
                    TempData["Success"] = "Người dùng đã được cập nhật!";
                }
                return RedirectToAction(nameof(Index));
            }
            return View(user);
        }

        // GET: Users/Delete/5
        [Route("Delete/{id}")]
        public IActionResult Delete(int id)
        {
            var user = _context.Users.Find(id);
            if (user == null) return NotFound();
            return View(user);
        }

        // POST: Users/Delete/5
        [HttpPost, ActionName("Delete")]
        [Route("Delete/{id}")]
        [ValidateAntiForgeryToken]
        public IActionResult DeleteConfirmed(int id)
        {
            var user = _context.Users.Find(id);
            if (user != null)
            {
                _context.Users.Remove(user);
                _context.SaveChanges();
                TempData["Success"] = "Người dùng đã được xóa!";
            }
            return RedirectToAction(nameof(Index));
        }

        // GET: Users/ChangePassword
        [Route("ChangePassword")]
        public IActionResult ChangePassword()
        {
            return View();
        }

        // POST: Users/ChangePassword
        [HttpPost]
        [Route("ChangePassword")]
        [ValidateAntiForgeryToken]
        public IActionResult ChangePassword(string currentPassword, string newPassword, string confirmPassword)
        {
            var username = HttpContext.Session.GetString("User");
            var user = _context.Users.FirstOrDefault(u => u.Username == username);

            if (user == null)
            {
                TempData["Error"] = "Người dùng không tồn tại!";
                return View();
            }

            // Kiểm tra mật khẩu hiện tại
            if (!BCrypt.Net.BCrypt.Verify(currentPassword, user.PasswordHash))
            {
                TempData["Error"] = "Mật khẩu hiện tại không đúng!";
                return View();
            }

            // Kiểm tra mật khẩu mới khớp
            if (newPassword != confirmPassword)
            {
                TempData["Error"] = "Mật khẩu mới không khớp!";
                return View();
            }

            // Cập nhật mật khẩu
            user.PasswordHash = BCrypt.Net.BCrypt.HashPassword(newPassword);
            _context.Update(user);
            _context.SaveChanges();

            TempData["Success"] = "Mật khẩu đã được thay đổi thành công!";
            return RedirectToAction("Dashboard", "Admin");
        }
    }
}
