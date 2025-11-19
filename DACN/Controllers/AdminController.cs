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
            
            // Thêm BOM cho UTF-8 để Excel nhận diện đúng encoding
            reportData.Append('\ufeff');
            
            if (type == "Attendance")
            {
                reportData.AppendLine("==========================================================");
                reportData.AppendLine("           BÁO CÁO ĐIỂM DANH NHÂN VIÊN");
                reportData.AppendLine($"           Từ ngày: {(startDate?.ToString("dd/MM/yyyy") ?? "Tất cả")} - Đến ngày: {(endDate?.ToString("dd/MM/yyyy") ?? "Tất cả")}");
                reportData.AppendLine($"           Ngày xuất: {DateTime.Now:dd/MM/yyyy HH:mm:ss}");
                reportData.AppendLine("==========================================================");
                reportData.AppendLine("");
                reportData.AppendLine("ID,Tên nhân viên,Ngày,Giờ,Trạng thái");
                
                var records = _context.AttendanceRecords
                    .Join(_context.Employees, r => r.EmployeeId, e => e.Id, (r, e) => new { r, e })
                    .Where(x => !startDate.HasValue || x.r.TimestampIn >= startDate)
                    .Where(x => !endDate.HasValue || x.r.TimestampIn <= endDate)
                    .OrderBy(x => x.r.TimestampIn)
                    .ToList();

                foreach (var item in records)
                {
                    string name = item.e.Name?.Replace("\"", "\"\"") ?? "";
                    string status = item.r.Status?.Replace("\"", "\"\"") ?? "present";
                    // Thêm dấu nháy đơn trước ngày để Excel hiểu là text
                    string dateOnly = item.r.TimestampIn.HasValue ? "'" + item.r.TimestampIn.Value.ToString("dd/MM/yyyy") : "";
                    string timeOnly = item.r.TimestampIn.HasValue ? "'" + item.r.TimestampIn.Value.ToString("HH:mm:ss") : "";
                    
                    reportData.AppendLine($"{item.r.Id},\"{name}\",{dateOnly},{timeOnly},\"{status}\"");
                }
                
                // Thêm footer
                reportData.AppendLine("");
                reportData.AppendLine("==========================================================");
                reportData.AppendLine($"           Tổng số bản ghi: {records.Count}");
                reportData.AppendLine("==========================================================");
            }
            else if (type == "Employee")
            {
                reportData.AppendLine("==========================================================");
                reportData.AppendLine("           DANH SÁCH NHÂN VIÊN CÔNG TY");
                reportData.AppendLine($"           Tổng số nhân viên: {_context.Employees.Count()} người");
                reportData.AppendLine($"           Ngày xuất: {DateTime.Now:dd/MM/yyyy HH:mm:ss}");
                reportData.AppendLine("==========================================================");
                reportData.AppendLine("");
                reportData.AppendLine("ID,Tên nhân viên,Phòng ban,Chức vụ,Số điện thoại,Email");
                
                var employees = _context.Employees
                    .OrderBy(e => e.Department)
                    .ThenBy(e => e.Name)
                    .ToList();
                
                foreach (var emp in employees)
                {
                    string name = emp.Name?.Replace("\"", "\"\"") ?? "";
                    string department = emp.Department?.Replace("\"", "\"\"") ?? "";
                    string role = emp.Role?.Replace("\"", "\"\"") ?? "";
                    // Thêm tab character (\t) trước số điện thoại để Excel hiểu là text
                    string phone = !string.IsNullOrEmpty(emp.Phone) ? $"\t{emp.Phone.Replace("\"", "\"\"")}" : "";
                    string email = emp.Email?.Replace("\"", "\"\"") ?? "";
                    
                    reportData.AppendLine($"{emp.Id},\"{name}\",\"{department}\",\"{role}\",\"{phone}\",\"{email}\"");
                }
                
                // Thêm footer với thống kê theo phòng ban
                reportData.AppendLine("");
                reportData.AppendLine("==========================================================");
                reportData.AppendLine("           THỐNG KÊ THEO PHÒNG BAN");
                reportData.AppendLine("==========================================================");
                
                var deptStats = _context.Employees
                    .GroupBy(e => e.Department)
                    .Select(g => new { Dept = g.Key ?? "Chưa phân công", Count = g.Count() })
                    .OrderByDescending(x => x.Count)
                    .ToList();
                
                foreach (var stat in deptStats)
                {
                    reportData.AppendLine($"           {stat.Dept}: {stat.Count} người");
                }
                reportData.AppendLine("==========================================================");
            }

            // Lưu file với encoding UTF-8 có BOM
            System.IO.File.WriteAllText(filePath, reportData.ToString(), new System.Text.UTF8Encoding(true));

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
            return File(fileBytes, "text/csv; charset=utf-8", fileName);
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