$env:PYTHONPATH = "D:\DACN"
cd D:\DACN
python -m uvicorn backend_src.app.main:app --host 0.0.0.0 --port 8000 --reload
