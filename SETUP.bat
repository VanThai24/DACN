@echo off
REM ========================================
REM  SETUP HỆ THỐNG ĐIỂM DANH - THESIS
REM ========================================

echo.
echo ========================================
echo  SETUP HỆ THỐNG ĐIỂM DANH
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long cai dat Python 3.8+
    pause
    exit /b 1
)

echo [1/5] Kiem tra Python... OK
echo.

REM Check MySQL
mysql --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] MySQL chua duoc cai dat!
    echo Vui long cai dat MySQL 8.0+
)

echo [2/5] Kiem tra MySQL... OK
echo.

REM Install Python dependencies
echo [3/5] Cai dat Python packages...
cd "%~dp0DACN\AI"
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Loi khi cai dat packages!
    pause
    exit /b 1
)
echo     Thanh cong!
echo.

REM Check trained model
if exist "faceid_best_model.pkl" (
    echo [4/5] Model da duoc train... OK
) else (
    echo [4/5] Model chua duoc train
    echo     Chay: python train_best_model.py
)
echo.

REM Check database
echo [5/5] Kiem tra database...
mysql -u root -p12345 -e "USE attendance_db; SELECT COUNT(*) FROM employees;" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Database chua duoc tao!
    echo Vui long chay backend va migration truoc
) else (
    echo     Database OK!
)
echo.

echo ========================================
echo  SETUP HOAN TAT!
echo ========================================
echo.
echo Cac lenh quan trong:
echo   - Chay Desktop App:  cd faceid_desktop ^& python main.py
echo   - Chay Web Admin:    cd DACN ^& dotnet run
echo   - Chay Mobile App:   cd mobile_app ^& npm start
echo   - Train Model:       cd AI ^& python train_best_model.py
echo   - Them Nhan Vien:    cd AI ^& .\add_new_employee.bat
echo.
pause
