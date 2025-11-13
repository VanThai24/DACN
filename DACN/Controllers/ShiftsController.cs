using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;

namespace Controllers
{
    public class ShiftsController : BaseAdminController
    {
        private readonly AppDbContext _context;
        public ShiftsController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {            var shifts = _context.Shifts
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

        // GET: Shifts/Details/5
        public IActionResult Details(int id)
        {            var shift = _context.Shifts
                .Where(s => s.Id == id)
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
                .FirstOrDefault();
            
            if (shift == null) return NotFound();
            return View(shift);
        }

        // GET: Shifts/Create
        public IActionResult Create()
        {            ViewBag.Employees = _context.Employees.ToList();
            return View();
        }

        // POST: Shifts/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Create(Shift shift)
        {            if (ModelState.IsValid)
            {
                _context.Shifts.Add(shift);
                _context.SaveChanges();
                return RedirectToAction(nameof(Index));
            }
            ViewBag.Employees = _context.Employees.ToList();
            return View(shift);
        }

        // GET: Shifts/Edit/5
        public IActionResult Edit(int id)
        {            var shift = _context.Shifts.Find(id);
            if (shift == null) return NotFound();
            
            ViewBag.Employees = _context.Employees.ToList();
            return View(shift);
        }

        // POST: Shifts/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Edit(int id, Shift shift)
        {            if (id != shift.Id) return NotFound();
            if (ModelState.IsValid)
            {
                _context.Update(shift);
                _context.SaveChanges();
                return RedirectToAction(nameof(Index));
            }
            ViewBag.Employees = _context.Employees.ToList();
            return View(shift);
        }

        // GET: Shifts/Delete/5
        public IActionResult Delete(int id)
        {            var shift = _context.Shifts.Find(id);
            if (shift == null) return NotFound();
            return View(shift);
        }

        // POST: Shifts/Delete/5
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public IActionResult DeleteConfirmed(int id)
        {            var shift = _context.Shifts.Find(id);
            if (shift != null)
            {
                _context.Shifts.Remove(shift);
                _context.SaveChanges();
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
