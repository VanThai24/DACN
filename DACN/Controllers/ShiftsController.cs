using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;

namespace Controllers
{
    public class ShiftsController : Controller
    {
        private readonly AppDbContext _context;
        public ShiftsController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var shifts = _context.Shifts
                .Join(_context.Employees,
                      s => s.EmployeeId,
                      e => e.Id,
                      (s, e) => new ShiftViewModel {
                          Id = s.Id,
                          EmployeeName = e.Name,
                          Date = s.Date,
                          StartTime = s.StartTime,
                          EndTime = s.EndTime
                      })
                .ToList();
            return View(shifts);
        }
    }
}
