@echo off
echo ========================================
echo DACN - Mobile App Connection Test
echo ========================================
echo.

echo [1] Checking IP Address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    echo    IP: %%a
)
echo.

echo [2] Testing Backend Health...
curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Backend is running on localhost:8000
) else (
    echo    [ERROR] Backend is NOT running on localhost:8000
    echo    Please start backend first: D:\DACN\DACN\backend_src\start_backend.bat
)
echo.

echo [3] Testing Backend API Docs...
curl -s http://localhost:8000/docs > nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] API Documentation available at http://localhost:8000/docs
) else (
    echo    [ERROR] Cannot access API docs
)
echo.

echo ========================================
echo Configuration:
echo ========================================
echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Mobile App Config:
echo File: D:\DACN\DACN\mobile_app\config.js
echo.
type D:\DACN\DACN\mobile_app\config.js
echo.
echo ========================================
echo.
pause
