using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace Controllers
{
    public class BaseAdminController : Controller
    {
        public override void OnActionExecuting(ActionExecutingContext context)
        {
            var user = HttpContext.Session.GetString("User");
            var userRole = HttpContext.Session.GetString("UserRole");

            // Nếu chưa đăng nhập hoặc không phải Admin/Manager -> redirect về login
            if (string.IsNullOrEmpty(user) || 
                (userRole != "Admin" && userRole != "Manager"))
            {
                context.Result = new RedirectResult("/Account/Login");
                return;
            }

            base.OnActionExecuting(context);
        }
    }
}
