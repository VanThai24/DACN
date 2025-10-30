using Microsoft.AspNetCore.Mvc;
using Data;
using Models;
using System.Linq;

namespace Controllers
{
    public class DevicesController : Controller
    {
        private readonly AppDbContext _context;
        public DevicesController(AppDbContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            if (HttpContext.Session.GetString("User") == null)
                return Redirect("/Account/Login");
            var devices = _context.Devices.ToList();
            return View(devices);
        }
    }
}
