@echo off
cd /d D:\DACN\DACN\backend_src
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
