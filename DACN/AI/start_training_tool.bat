@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════
echo  🎯 CÔNG CỤ THU THẬP DỮ LIỆU TRAINING - FACE RECOGNITION
echo ═══════════════════════════════════════════════════════════════
echo.
echo Chức năng:
echo   1. Kiểm tra dữ liệu hiện tại
echo   2. Thu thập ảnh training (TỰ ĐỘNG)
echo   3. Train model mới
echo   4. Test hệ thống
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

:menu
echo.
echo Chọn chức năng:
echo   [1] Kiểm tra dữ liệu (check_data.py)
echo   [2] Thu thập ảnh training (capture_training_data.py)
echo   [3] Tăng cường dữ liệu - Augmentation (augment_data.py) ⭐NEW
echo   [4] Tạo dữ liệu giả - Dummy Data (create_dummy_data.py) ⭐NEW
echo   [5] Train model (train_best_model.py)
echo   [6] Update embeddings (update_embeddings_best_model.py)
echo   [7] Test Desktop App
echo   [0] Thoát
echo.

set /p choice="Nhập lựa chọn (0-7): "

if "%choice%"=="1" goto check_data
if "%choice%"=="2" goto capture_data
if "%choice%"=="3" goto augment_data
if "%choice%"=="4" goto dummy_data
if "%choice%"=="5" goto train_model
if "%choice%"=="6" goto update_embeddings
if "%choice%"=="7" goto test_app
if "%choice%"=="0" goto end

echo ❌ Lựa chọn không hợp lệ!
goto menu

:check_data
echo.
echo 📊 Đang kiểm tra dữ liệu...
echo ───────────────────────────────────────────────────────────────
python check_data.py
pause
goto menu

:capture_data
echo.
echo 📸 Thu thập ảnh training
echo ───────────────────────────────────────────────────────────────
echo 💡 Hướng dẫn:
echo    - Nhấn SPACE để chụp mỗi ảnh
echo    - Làm theo hướng dẫn trên màn hình về góc độ
echo    - Đảm bảo ánh sáng tốt, khuôn mặt rõ nét
echo.
python capture_training_data.py
pause
goto menu

:augment_data
echo.
echo 🎨 Tăng cường dữ liệu (Augmentation)
echo ───────────────────────────────────────────────────────────────
echo 💡 Từ 10 ảnh gốc → Tạo thành 50 ảnh
echo    Phù hợp khi chỉ có ít nhân viên
echo.
python augment_data.py
pause
goto menu

:dummy_data
echo.
echo 🎭 Tạo dữ liệu giả (Dummy Data)
echo ───────────────────────────────────────────────────────────────
echo ⚠️  CHỈ dùng để TEST/DEMO
echo    KHÔNG dùng trong production!
echo.
python create_dummy_data.py
pause
goto menu

:train_model
echo.
echo 🔄 Train model mới
echo ───────────────────────────────────────────────────────────────
echo ⚠️  Lưu ý: Đảm bảo đã thu thập đủ 30-50 ảnh/người
echo.
set /p confirm="Tiếp tục train model? (y/n): "
if /i "%confirm%"=="y" (
    python train_best_model.py
    echo.
    echo ✅ Đã train xong! Tiếp tục update embeddings...
    pause
    python update_embeddings_best_model.py
) else (
    echo ❌ Đã hủy!
)
pause
goto menu

:update_embeddings
echo.
echo 🔄 Update embeddings
echo ───────────────────────────────────────────────────────────────
python update_embeddings_best_model.py
pause
goto menu

:test_app
echo.
echo 🧪 Test Desktop App
echo ───────────────────────────────────────────────────────────────
cd ..\faceid_desktop
python main.py
cd ..\AI
pause
goto menu

:end
echo.
echo 👋 Cảm ơn đã sử dụng! Bye bye!
echo.
exit
