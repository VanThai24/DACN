using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;

namespace Controllers
{
    public class DevicesController : BaseAdminController
    {
        private readonly AppDbContext _context;
        public DevicesController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {            var devices = _context.Devices.ToList();
            return View(devices);
        }

        // GET: Devices/Details/5
        public IActionResult Details(int id)
        {            var device = _context.Devices.Find(id);
            if (device == null) return NotFound();
            return View(device);
        }

        // GET: Devices/Create
        public IActionResult Create()
        {            return View();
        }

        // POST: Devices/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Create(Device device)
        {            if (ModelState.IsValid)
            {
                // Tự động sinh API Key
                device.ApiKey = Guid.NewGuid().ToString();
                device.LastSeen = DateTime.Now;
                _context.Devices.Add(device);
                _context.SaveChanges();
                return RedirectToAction(nameof(Index));
            }
            return View(device);
        }

        // GET: Devices/Edit/5
        public IActionResult Edit(int id)
        {            var device = _context.Devices.Find(id);
            if (device == null) return NotFound();
            return View(device);
        }

        // POST: Devices/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public IActionResult Edit(int id, Device device)
        {            if (id != device.Id) return NotFound();
            if (ModelState.IsValid)
            {
                _context.Update(device);
                _context.SaveChanges();
                return RedirectToAction(nameof(Index));
            }
            return View(device);
        }

        // GET: Devices/Delete/5
        public IActionResult Delete(int id)
        {            var device = _context.Devices.Find(id);
            if (device == null) return NotFound();
            return View(device);
        }

        // POST: Devices/Delete/5
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public IActionResult DeleteConfirmed(int id)
        {            var device = _context.Devices.Find(id);
            if (device != null)
            {
                _context.Devices.Remove(device);
                _context.SaveChanges();
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
