@echo off
chcp 65001 >nul
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo  🎓 QUICK SETUP CHO ĐỒ ÁN CHUYÊN NGÀNH
echo ═══════════════════════════════════════════════════════════════
echo.
echo Script này sẽ:
echo   1. Kiểm tra dữ liệu hiện tại
echo   2. Train model với data có sẵn
echo   3. Test Desktop app
echo.
echo Thời gian: Khoảng 5 phút
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause

echo.
echo [1/4] Kiểm tra dữ liệu hiện tại...
echo ───────────────────────────────────────────────────────────────
python check_data.py

echo.
echo.
set /p continue="Tiếp tục train với data hiện tại? (y/n): "
if /i not "%continue%"=="y" (
    echo.
    echo ❌ Đã hủy! Nếu muốn thêm data, chạy:
    echo    python augment_data.py
    pause
    exit
)

echo.
echo [2/4] Training model...
echo ───────────────────────────────────────────────────────────────
python train_best_model.py

if errorlevel 1 (
    echo.
    echo ❌ Training thất bại! Check logs ở trên.
    pause
    exit
)

echo.
echo [3/4] Update embeddings...
echo ───────────────────────────────────────────────────────────────
python update_embeddings_best_model.py

if errorlevel 1 (
    echo.
    echo ❌ Update embeddings thất bại!
    pause
    exit
)

echo.
echo [4/4] Mở Desktop app để test...
echo ───────────────────────────────────────────────────────────────
echo.
echo 💡 Hướng dẫn test:
echo    - Bật camera
echo    - Di chuyển khuôn mặt vào khung hình
echo    - Nhấn SPACE để điểm danh
echo.
timeout /t 3 /nobreak >nul

cd ..\faceid_desktop
start python main.py
cd ..\AI

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ HOÀN TẤT!
echo ═══════════════════════════════════════════════════════════════
echo.
echo Desktop app đã được mở trong cửa sổ mới.
echo.
echo 📝 Các bước tiếp theo:
echo    1. Test điểm danh với Desktop app
echo    2. Check admin web: http://localhost:5000
echo    3. Test mobile app (nếu cần)
echo.
echo 🎯 Cho đồ án:
echo    - Đã đủ để demo và bảo vệ
echo    - Nếu muốn "đẹp" hơn: chạy python augment_data.py
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
