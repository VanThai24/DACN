using System.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using AdminWeb.Models;

namespace AdminWeb.Controllers;

public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;

    public HomeController(ILogger<HomeController> logger)
    {
        _logger = logger;
    }

    public IActionResult Index()
    {
        if (HttpContext.Session.GetString("User") == null)
            return Redirect("/Account/Login");
        return View();
    }

    public IActionResult Privacy()
    {
        if (HttpContext.Session.GetString("User") == null)
            return Redirect("/Account/Login");
        return View();
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
