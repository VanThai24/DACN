# Script restart Web Admin với code mới
Write-Host "Đang dừng Web Admin..." -ForegroundColor Yellow
Get-Process -Name "AdminWeb" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "Đang build lại project..." -ForegroundColor Cyan
dotnet build AdminWeb.csproj

Write-Host "`nĐang khởi động Web Admin..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd D:\DACN\DACN; dotnet run" -WindowStyle Minimized

Start-Sleep -Seconds 5
Write-Host "`n✅ Web Admin đã được restart!" -ForegroundColor Green
Write-Host "Truy cập: http://localhost:5280" -ForegroundColor Cyan
