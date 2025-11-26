using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;
using X.PagedList;
using Microsoft.AspNetCore.Authorization;

namespace Controllers
{
    public class AttendanceController : BaseAdminController
    {
        private readonly AppDbContext _context;
        public AttendanceController(AppDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        [AllowAnonymous] // Cho phép truy cập API từ client
        public IActionResult AttendanceStats(string date)
        {
            var query = _context.AttendanceRecords.AsQueryable();
            if (!string.IsNullOrEmpty(date) && DateTime.TryParse(date, out var d))
                query = query.Where(x => x.TimestampIn.HasValue && x.TimestampIn.Value.Date == d.Date);

            var stats = query
                .Where(x => !string.IsNullOrEmpty(x.Status))
                .GroupBy(x => x.Status ?? "unknown")
                .Select(g => new { Status = g.Key, Count = g.Count() })
                .ToList();
            return Json(stats);
        }

        public IActionResult Index(string employee, string status, string date, int? page)
        {
            var query = _context.AttendanceRecords
                .Join(_context.Employees,
                      r => r.EmployeeId,
                      e => e.Id,
                      (r, e) => new AttendanceRecordViewModel {
                          Id = r.Id,
                          EmployeeName = e.Name,
                          TimestampIn = r.TimestampIn,
                          Status = r.Status,
                          PhotoPath = r.PhotoPath,
                          DeviceId = r.DeviceId
                      });

            if (!string.IsNullOrEmpty(employee))
                query = query.Where(x => x.EmployeeName.Contains(employee));
            if (!string.IsNullOrEmpty(status))
                query = query.Where(x => x.Status == status);
            if (!string.IsNullOrEmpty(date) && DateTime.TryParse(date, out var d))
                query = query.Where(x => x.TimestampIn.HasValue && x.TimestampIn.Value.Date == d.Date);

            int pageSize = 10;
            int pageNumber = page ?? 1;
            var paged = query.OrderByDescending(x => x.TimestampIn).ToList().ToPagedList(pageNumber, pageSize);
            return View(paged);
        }

            // GET: Attendance/Details/5
            public IActionResult Details(int id)
            {
                var record = _context.AttendanceRecords
                    .Where(r => r.Id == id)
                    .Join(_context.Employees,
                          r => r.EmployeeId,
                          e => e.Id,
                          (r, e) => new AttendanceRecordViewModel {
                              Id = r.Id,
                              EmployeeName = e.Name,
                              TimestampIn = r.TimestampIn,
                              Status = r.Status,
                              PhotoPath = r.PhotoPath,
                              DeviceId = r.DeviceId
                          })
                    .FirstOrDefault();
                if (record == null) return NotFound();
                return View(record);
            }

            // GET: Attendance/Create
            public IActionResult Create()
            {
                return View();
            }

            // POST: Attendance/Create
            [HttpPost]
            [ValidateAntiForgeryToken]
            public IActionResult Create(AttendanceRecord record)
            {
                if (ModelState.IsValid)
                {
                    _context.AttendanceRecords.Add(record);
                    _context.SaveChanges();
                    return RedirectToAction(nameof(Index));
                }
                return View(record);
            }

            // GET: Attendance/Edit/5
            public IActionResult Edit(int id)
            {
                var record = _context.AttendanceRecords.Find(id);
                if (record == null) return NotFound();
                return View(record);
            }

            // POST: Attendance/Edit/5
            [HttpPost]
            [ValidateAntiForgeryToken]
            public IActionResult Edit(int id, AttendanceRecord record)
            {
                if (id != record.Id) return NotFound();
                if (ModelState.IsValid)
                {
                    _context.Update(record);
                    _context.SaveChanges();
                    return RedirectToAction(nameof(Index));
                }
                return View(record);
            }

            // GET: Attendance/Delete/5
            public IActionResult Delete(int id)
            {
                var record = _context.AttendanceRecords.Find(id);
                if (record == null) return NotFound();
                return View(record);
            }

            // POST: Attendance/Delete/5
            [HttpPost, ActionName("Delete")]
            [ValidateAntiForgeryToken]
            public IActionResult DeleteConfirmed(int id)
            {
                var record = _context.AttendanceRecords.Find(id);
                if (record != null)
                {
                    _context.AttendanceRecords.Remove(record);
                    _context.SaveChanges();
                }
                return RedirectToAction(nameof(Index));
            }
    }
}
