# Automatic Setup Script for DACN Project
# Run this script to setup everything automatically

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "DACN Project - Automatic Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
$backendPath = Join-Path $PSScriptRoot "backend_src"
Set-Location $backendPath

Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[5/5] Running tests..." -ForegroundColor Yellow
pytest tests/ -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All tests passed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some tests failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Edit .env file if needed" -ForegroundColor White
Write-Host "2. Start backend: python -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "3. Start AI backend: cd ../AI && python app.py" -ForegroundColor White
Write-Host "4. Visit API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
