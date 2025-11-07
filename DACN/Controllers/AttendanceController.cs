using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;

namespace Controllers
{
    public class AttendanceController : Controller
    {
        private readonly AppDbContext _context;
        public AttendanceController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var records = _context.AttendanceRecords
                .Join(_context.Employees,
                      r => r.EmployeeId,
                      e => e.Id,
                      (r, e) => new AttendanceRecordViewModel {
                          Id = r.Id,
                          EmployeeName = e.Name,
                          TimestampIn = r.TimestampIn,
                          // TimestampOut = r.TimestampOut, // Đã xóa cột timestamp_out khỏi database
                          Status = r.Status,
                          PhotoPath = r.PhotoPath,
                          DeviceId = r.DeviceId
                      })
                .ToList();
            return View(records);
        }
    }
}
