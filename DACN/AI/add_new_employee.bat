@echo off
chcp 65001 >nul
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo  👤 THÊM NHÂN VIÊN MỚI VÀO HỆ THỐNG
echo ═══════════════════════════════════════════════════════════════
echo.
echo Quy trình:
echo   1. Chụp ảnh nhân viên mới (10-20 ảnh)
echo   2. Augment data lên 40 ảnh
echo   3. Retrain model
echo   4. Update embeddings
echo.
echo Thời gian: ~10 phút
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause

echo.
echo [1/4] Chụp ảnh nhân viên mới...
echo ───────────────────────────────────────────────────────────────
echo 💡 Hướng dẫn:
echo    - Nhập tên nhân viên (VD: Minh, Nam, Trang)
echo    - Nhập số ảnh: 15-20 (đủ để augment)
echo    - Nhấn SPACE để chụp mỗi ảnh
echo    - Làm theo hướng dẫn về góc độ
echo.
python capture_training_data.py

if errorlevel 1 (
    echo.
    echo ❌ Chụp ảnh thất bại!
    pause
    exit
)

echo.
echo.
set /p person_name="Nhập lại tên nhân viên vừa chụp: "

echo.
echo [2/4] Augment data lên 40 ảnh...
echo ───────────────────────────────────────────────────────────────
python -c "from augment_data import augment_person_data; augment_person_data('%person_name%', 40)"

echo.
echo [3/4] Retrain model với nhân viên mới...
echo ───────────────────────────────────────────────────────────────
python train_best_model.py

if errorlevel 1 (
    echo.
    echo ❌ Training thất bại!
    pause
    exit
)

echo.
echo [4/4] Update embeddings vào database...
echo ───────────────────────────────────────────────────────────────
python update_embeddings_best_model.py

if errorlevel 1 (
    echo.
    echo ❌ Update embeddings thất bại!
    pause
    exit
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ HOÀN TẤT! NHÂN VIÊN MỚI ĐÃ ĐƯỢC THÊM VÀO HỆ THỐNG
echo ═══════════════════════════════════════════════════════════════
echo.
echo Nhân viên: %person_name%
echo.
echo 🎯 Bước tiếp theo:
echo    1. Test Desktop app: python main.py
echo    2. Hoặc thêm nhân viên khác: chạy lại script này
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
