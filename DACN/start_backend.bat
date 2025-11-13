@echo off
REM Script khởi động Backend API cho AdminWeb có thể kết nối

echo ========================================
echo   Khởi động Backend API (Port 8000)
echo ========================================
echo.

cd /d D:\DACN\DACN

echo [1/4] Kich hoat Python virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/4] Checking dependencies...
python --version
echo.

echo [3/4] Checking MySQL connection...
echo Database: mysql://root:***@127.0.0.1:3306/attendance_db
echo.

echo [4/4] Khoi dong FastAPI server...
echo Server se chay tai: http://0.0.0.0:8000
echo API Docs: http://localhost:8000/docs
echo Nhan Ctrl+C de dung server
echo.

REM Chạy uvicorn với reload để tự động restart khi code thay đổi
venv\Scripts\python.exe -m uvicorn backend_src.app.main:app --reload --host 0.0.0.0 --port 8000

pause
