using Microsoft.AspNetCore.Mvc;
using Data;
using System.Linq;

namespace Controllers
{
    public class AdminController : Controller
    {
        private readonly AppDbContext _context;
        public AdminController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Dashboard()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var employeeCount = _context.Employees.Count();
            var attendanceCount = _context.AttendanceRecords.Count();
            var reportCount = _context.Reports.Count();
            ViewBag.EmployeeCount = employeeCount;
            ViewBag.AttendanceCount = attendanceCount;
            ViewBag.ReportCount = reportCount;
            return View();
        }

        public IActionResult Employees()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var employees = _context.Employees.ToList();
            return View(employees);
        }

        public IActionResult Faces()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            return View();
        }

        public IActionResult Reports()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var reports = _context.Reports.ToList();
            return View(reports);
        }
    }
}
