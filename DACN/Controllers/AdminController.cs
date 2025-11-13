using Microsoft.AspNetCore.Mvc;
using Data;
using System.Linq;

namespace Controllers
{
    public class AdminController : BaseAdminController
    {
        private readonly AppDbContext _context;
        public AdminController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Dashboard()
        {
            // Thống kê cơ bản
            var employeeCount = _context.Employees.Count();
            var attendanceCount = _context.AttendanceRecords.Count();
            var reportCount = _context.Reports.Count();
            var deviceCount = _context.Devices.Count();
            
            ViewBag.EmployeeCount = employeeCount;
            ViewBag.AttendanceCount = attendanceCount;
            ViewBag.ReportCount = reportCount;
            ViewBag.DeviceCount = deviceCount;

            // Thống kê theo phòng ban
            var departmentStats = _context.Employees
                .GroupBy(e => e.Department)
                .Select(g => new { Department = g.Key, Count = g.Count() })
                .ToList();
            ViewBag.DepartmentStats = departmentStats;

            // Điểm danh hôm nay
            var today = DateTime.Today;
            var todayAttendance = _context.AttendanceRecords
                .Where(r => r.TimestampIn.HasValue && r.TimestampIn.Value.Date == today)
                .Count();
            ViewBag.TodayAttendance = todayAttendance;

            // Top 5 nhân viên đi muộn (giả sử ca bắt đầu 8:00)
            var lateEmployees = _context.AttendanceRecords
                .Where(r => r.TimestampIn.HasValue && r.TimestampIn.Value.TimeOfDay > new TimeSpan(8, 0, 0))
                .Join(_context.Employees, r => r.EmployeeId, e => e.Id, (r, e) => new { 
                    Name = e.Name, 
                    Time = r.TimestampIn 
                })
                .OrderByDescending(x => x.Time)
                .Take(5)
                .ToList();
            ViewBag.LateEmployees = lateEmployees;

            // Thống kê điểm danh 7 ngày gần đây
            var last7Days = Enumerable.Range(0, 7)
                .Select(i => today.AddDays(-i))
                .Reverse()
                .ToList();
            
            var dailyAttendance = last7Days.Select(date => new {
                Date = date.ToString("dd/MM"),
                Count = _context.AttendanceRecords
                    .Count(r => r.TimestampIn.HasValue && r.TimestampIn.Value.Date == date)
            }).ToList();
            
            ViewBag.DailyAttendance = dailyAttendance;
            
            return View();
        }

        public IActionResult Employees()
        {
            var employees = _context.Employees.ToList();
            return View(employees);
        }

        public IActionResult Faces()
        {
            // Lấy danh sách employees có face embedding
            var employeesWithFaces = _context.Employees
                .Where(e => e.FaceEmbedding != null)
                .Select(e => new { 
                    Id = e.Id, 
                    Name = e.Name,
                    PhotoPath = e.PhotoPath
                })
                .ToList();
            
            ViewBag.EmployeesWithFaces = employeesWithFaces;
            return View();
        }

        public IActionResult Reports()
        {
            var reports = _context.Reports.ToList();
            return View(reports);
        }

        // GET: Admin/CreateReport
        public IActionResult CreateReport()
        {
            return View();
        }

        // POST: Admin/CreateReport
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult CreateReport(string type, DateTime? startDate, DateTime? endDate)
        {
            var user = HttpContext.Session.GetString("User");
            var fileName = $"Report_{type}_{DateTime.Now:yyyyMMddHHmmss}.csv";
            var filePath = Path.Combine("wwwroot", "reports", fileName);

            // Tạo thư mục nếu chưa có
            Directory.CreateDirectory(Path.Combine("wwwroot", "reports"));

            // Tạo nội dung báo cáo
            var reportData = new System.Text.StringBuilder();
            reportData.AppendLine("ID,Name,Date,Status");

            if (type == "Attendance")
            {
                var records = _context.AttendanceRecords
                    .Join(_context.Employees, r => r.EmployeeId, e => e.Id, (r, e) => new { r, e })
                    .Where(x => !startDate.HasValue || x.r.TimestampIn >= startDate)
                    .Where(x => !endDate.HasValue || x.r.TimestampIn <= endDate)
                    .ToList();

                foreach (var item in records)
                {
                    reportData.AppendLine($"{item.r.Id},{item.e.Name},{item.r.TimestampIn:yyyy-MM-dd HH:mm},{item.r.Status}");
                }
            }
            else if (type == "Employee")
            {
                var employees = _context.Employees.ToList();
                reportData.Clear();
                reportData.AppendLine("ID,Name,Department,Role,Phone,Email");
                foreach (var emp in employees)
                {
                    reportData.AppendLine($"{emp.Id},{emp.Name},{emp.Department},{emp.Role},{emp.Phone},{emp.Email}");
                }
            }

            // Lưu file
            System.IO.File.WriteAllText(filePath, reportData.ToString());

            // Lưu thông tin báo cáo vào database
            var report = new Models.Report
            {
                Type = type,
                FilePath = $"/reports/{fileName}",
                CreatedAt = DateTime.Now,
                CreatedBy = 1 // TODO: Get actual user ID from session
            };
            _context.Reports.Add(report);
            _context.SaveChanges();

            TempData["Success"] = "Báo cáo đã được tạo thành công!";
            return RedirectToAction(nameof(Reports));
        }

        // GET: Admin/DownloadReport/5
        public IActionResult DownloadReport(int id)
        {
            var report = _context.Reports.Find(id);
            if (report == null || report.FilePath == null) return NotFound();

            var filePath = Path.Combine("wwwroot", report.FilePath.TrimStart('/'));
            if (!System.IO.File.Exists(filePath))
                return NotFound("File không tồn tại");

            var fileBytes = System.IO.File.ReadAllBytes(filePath);
            var fileName = Path.GetFileName(filePath);
            return File(fileBytes, "text/csv", fileName);
        }

        // POST: Admin/DeleteReport/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult DeleteReport(int id)
        {
            var report = _context.Reports.Find(id);
            if (report != null && report.FilePath != null)
            {
                // Xóa file nếu tồn tại
                var filePath = Path.Combine("wwwroot", report.FilePath.TrimStart('/'));
                if (System.IO.File.Exists(filePath))
                {
                    System.IO.File.Delete(filePath);
                }

                _context.Reports.Remove(report);
                _context.SaveChanges();
                TempData["Success"] = "Báo cáo đã được xóa!";
            }
            return RedirectToAction(nameof(Reports));
        }
    }
}
