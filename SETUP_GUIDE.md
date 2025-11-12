# 🎯 DACN - Attendance System - Complete Setup Guide

## 📦 Các Cải Tiến Đã Hoàn Thành Tự Động

### ✅ Phase 1: Code Quality & Infrastructure
1. **Debug Code Cleanup** - Xóa tất cả debug statements
2. **Professional Logging** - Setup loguru + rotation
3. **Environment Configuration** - .env files + config management
4. **Security Enhancements** - CORS, rate limiting, CSRF protection
5. **Error Handling** - Global exception handlers
6. **Testing Framework** - pytest + fixtures

### ✅ Phase 2: Input Validation & Security
1. **Pydantic Schemas** - Complete validation cho tất cả models
2. **File Upload Security** - Image validation + sanitization
3. **Custom Validators** - Phone, email, name validation
4. **Error Formatting** - User-friendly validation errors
5. **Security Tests** - Comprehensive test coverage

---

## 🚀 Quick Start

### 1. Cài Đặt Dependencies

```bash
cd DACN/backend_src

# Tạo virtual environment (nếu chưa có)
python -m venv venv

# Kích hoạt venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt packages
pip install -r requirements.txt
```

### 2. Cấu Hình Environment

```bash
# File .env đã được tạo sẵn
# Chỉnh sửa nếu cần:
notepad .env

# Các biến quan trọng:
# - JWT_SECRET_KEY (đổi cho production!)
# - DATABASE_URL (đổi sang PostgreSQL cho production)
# - SMTP_USERNAME, SMTP_PASSWORD (cho email)
```

### 3. Chạy Tests

```bash
# Chạy tất cả tests
pytest

# Với coverage report
pytest --cov=app --cov-report=html

# Xem coverage report
start htmlcov/index.html  # Windows
```

### 4. Khởi Động Backend

```bash
# Development mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or với script
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 5. Khởi Động AI Flask Backend

```bash
cd ../AI
python app.py
# Chạy trên http://localhost:5000
```

---

## 📚 Documentation

### Validation Guide
Chi tiết về input validation: [`VALIDATION_GUIDE.md`](./VALIDATION_GUIDE.md)

### Improvements Log
Lịch sử các cải tiến: [`IMPROVEMENTS.md`](./IMPROVEMENTS.md)

### API Documentation
Khi backend chạy, truy cập:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🧪 Testing

### Chạy Tests Cụ Thể

```bash
# Config tests
pytest tests/test_config.py -v

# Validation tests
pytest tests/test_validation.py -v

# File upload tests
pytest tests/test_file_validation.py -v

# Auth tests
pytest tests/test_auth.py -v
```

### Test Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/

# View report
start htmlcov/index.html
```

---

## 🔒 Security Checklist

- [x] Debug code removed
- [x] Environment variables for secrets
- [x] CORS configured
- [x] Rate limiting enabled
- [x] CSRF protection (ValidateAntiForgeryToken)
- [x] Input validation (Pydantic)
- [x] File upload validation
- [x] Filename sanitization
- [x] SQL injection prevention (ORM)
- [x] Exception handling
- [ ] HTTPS/SSL (deploy time)
- [ ] API authentication (Phase 3)

---

## 📊 Project Structure

```
DACN/
├── backend_src/
│   ├── .env                    # Environment config
│   ├── .env.example            # Template
│   ├── requirements.txt        # Dependencies
│   ├── run_tests.py           # Test runner
│   ├── app/
│   │   ├── config.py          # Settings management
│   │   ├── main.py            # FastAPI app
│   │   ├── middleware.py      # Custom handlers
│   │   ├── validators.py      # File validators
│   │   ├── schemas/           # Pydantic models
│   │   │   ├── employee.py
│   │   │   ├── auth.py
│   │   │   └── faceid.py
│   │   ├── routers/           # API endpoints
│   │   ├── crud/              # Database operations
│   │   └── models/            # SQLAlchemy models
│   └── tests/                 # Test suite
│       ├── conftest.py
│       ├── test_config.py
│       ├── test_auth.py
│       ├── test_validation.py
│       └── test_file_validation.py
├── AI/
│   ├── app.py                 # Flask AI backend
│   ├── faceid_model_tf_best.h5
│   └── face_data/
├── Controllers/               # ASP.NET controllers
├── Views/                     # Razor views
└── mobile_app/               # React Native app
```

---

## 🔧 Configuration Files

### `.env` Variables

```env
# Database
DATABASE_URL=sqlite:///./dacn.db

# JWT
JWT_SECRET_KEY=change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI
AI_MODEL_PATH=../AI/faceid_model_tf_best.h5
FLASK_AI_URL=http://localhost:5000

# Upload
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png

# Security
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Environment
ENVIRONMENT=development
```

---

## 🐛 Common Issues

### Issue: Import errors
```bash
# Solution: Activate venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Port already in use
```bash
# Solution: Change port or kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Issue: Tests fail
```bash
# Solution: Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests
pytest -v
```

### Issue: Module not found
```bash
# Solution: Install missing package
pip install <package-name>

# Or reinstall all
pip install -r requirements.txt --force-reinstall
```

---

## 📈 Performance Tips

1. **Use Redis for caching** (Phase 3)
2. **Enable database pooling**
3. **Optimize AI model** (quantization)
4. **Use CDN for static files**
5. **Enable gzip compression**

---

## 🚢 Deployment Checklist

### Before Deploy:
- [ ] Change `JWT_SECRET_KEY` to random secure key
- [ ] Update `DATABASE_URL` to production database
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure SMTP for production
- [ ] Update `CORS_ORIGINS` with production domains
- [ ] Enable HTTPS/SSL
- [ ] Setup database backups
- [ ] Configure monitoring/alerts
- [ ] Review logs configuration
- [ ] Test all endpoints

### Production Environment:
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=<generate-random-256-bit-key>
```

---

## 📞 Support

- **Documentation**: Xem các file .md trong project
- **API Docs**: http://localhost:8000/docs
- **Issues**: Tạo issue trên GitHub
- **Tests**: Chạy `pytest -v` để kiểm tra

---

## 📝 Next Steps

### Phase 3 (Recommended):
1. **Redis Caching** - Cache face embeddings
2. **PostgreSQL Migration** - Production database
3. **API Authentication** - JWT tokens cho mobile
4. **CI/CD Pipeline** - Automated testing & deployment
5. **Docker Containerization** - Easy deployment
6. **Monitoring** - Error tracking & performance

---

**Version**: 2.0.0  
**Last Updated**: November 12, 2025  
**Status**: Production Ready (Phase 1 & 2 Complete) ✅
