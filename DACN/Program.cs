using Microsoft.EntityFrameworkCore;
using System;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSession();

// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddDbContext<Data.AppDbContext>(options =>
    options.UseMySql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        new MySqlServerVersion(new Version(8, 0, 36)) // Sửa version cho đúng với MySQL của bạn
    )
);

var app = builder.Build();
app.UseSession();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

// app.UseHttpsRedirection();
app.UseRouting();

app.UseAuthorization();

app.MapStaticAssets();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Admin}/{action=Dashboard}/{id?}")
    .WithStaticAssets();

app.MapControllerRoute(
    name: "devices",
    pattern: "Admin/Devices/{action=Index}/{id?}",
    defaults: new { controller = "Devices" });
app.MapControllerRoute(
    name: "attendance",
    pattern: "Admin/Attendance/{action=Index}/{id?}",
    defaults: new { controller = "Attendance" });
app.MapControllerRoute(
    name: "shifts",
    pattern: "Admin/Shifts/{action=Index}/{id?}",
    defaults: new { controller = "Shifts" });
app.MapControllerRoute(
    name: "employees",
    pattern: "Employees/{action=Index}/{id?}",
    defaults: new { controller = "Employees" });


app.Run();
