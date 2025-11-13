# Script tự động khởi động Flask AI Server
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Flask AI Server - FaceID v2.0" -ForegroundColor Cyan
Write-Host "  Cosine Similarity + MobileNetV2" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Kiểm tra model
$modelBest = "D:\DACN\DACN\AI\faceid_model_tf_best.h5"
$modelNormal = "D:\DACN\DACN\AI\faceid_model_tf.h5"

if (Test-Path $modelBest) {
    Write-Host "✓ Found best model: faceid_model_tf_best.h5" -ForegroundColor Green
} elseif (Test-Path $modelNormal) {
    Write-Host "✓ Found model: faceid_model_tf.h5" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: No model found!" -ForegroundColor Red
    Write-Host "  Please train model first: python train_faceid_improved_v2.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting Flask server on http://127.0.0.1:5000 ..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Chạy server
Set-Location D:\DACN\DACN\AI
D:\DACN\DACN\venv\Scripts\python.exe app.py
