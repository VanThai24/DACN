# Quick Start Commands

## Development Setup (Windows)

### Prerequisites Check
```powershell
# Check Python version (need 3.9+)
python --version

# Check Docker (optional, for Redis/PostgreSQL)
docker --version
docker-compose --version
```

### Install Dependencies
```powershell
cd D:\DACN\DACN\backend_src

# Install Python packages
pip install -r requirements.txt
```

### Configure Environment
```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env with your settings (optional)
notepad .env
```

### Start Services (Option 1: Docker - Recommended)
```powershell
# Start Redis and PostgreSQL
docker-compose up -d postgres redis

# Wait 10 seconds for services to start
Start-Sleep -Seconds 10

# Run database migrations
alembic upgrade head
```

### Start Services (Option 2: Local SQLite)
```powershell
# No additional services needed
# SQLite database will be created automatically

# Run database migrations
alembic upgrade head
```

### Start Backend Server
```powershell
# Start FastAPI backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start AI Backend (Separate Terminal)
```powershell
cd D:\DACN\DACN\AI

# Install AI dependencies (if not already installed)
pip install flask tensorflow opencv-python-headless numpy Pillow

# Start Flask AI backend
python app.py
```

### Verify Installation
```powershell
# Test backend API
curl http://localhost:8000/docs

# Test AI backend
curl http://localhost:5000/health
```

---

## Production Deployment (Docker)

### Quick Deploy
```powershell
cd D:\DACN\DACN\backend_src

# Copy and configure environment
Copy-Item .env.example .env
# Edit .env with production settings

# Start all services (backend, AI, PostgreSQL, Redis)
docker-compose up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

# Check status
docker-compose ps
```

### Verify Deployment
```powershell
# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f

# Test backend
curl http://localhost:8000/health

# Test AI backend
curl http://localhost:5000/health
```

---

## Testing

### Run All Tests
```powershell
cd D:\DACN\DACN\backend_src

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
Start-Process htmlcov/index.html
```

---

## Common Operations

### Database Operations
```powershell
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

### Docker Operations
```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# View logs
docker-compose logs -f backend

# Restart service
docker-compose restart backend

# Remove everything
docker-compose down -v
```

### Cache Operations
```powershell
# Clear Redis cache
docker-compose exec redis redis-cli -a dacn_redis_password FLUSHDB

# View cache stats
docker-compose exec redis redis-cli -a dacn_redis_password INFO stats

# View cached keys
docker-compose exec redis redis-cli -a dacn_redis_password KEYS "*"
```

### Database Backup
```powershell
# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U dacn_user dacn_db > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Restore from backup
Get-Content backup.sql | docker-compose exec -T postgres psql -U dacn_user -d dacn_db
```

---

## Troubleshooting

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Redis Connection Error
```powershell
# Check Redis is running
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# View Redis logs
docker-compose logs redis
```

### Database Connection Error
```powershell
# Check PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# View PostgreSQL logs
docker-compose logs postgres
```

### Reset Everything
```powershell
# Stop and remove all containers
docker-compose down -v

# Remove database file (if using SQLite)
Remove-Item dacn.db -ErrorAction SilentlyContinue

# Start fresh
docker-compose up -d
alembic upgrade head
```

---

## Service URLs

After starting services, access:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc
- **AI Backend**: http://localhost:5000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## Environment Variables Reference

### Required
```env
DATABASE_URL=sqlite:///./dacn.db                    # Or PostgreSQL URL
JWT_SECRET_KEY=your-secret-key-here                 # Change in production
```

### Optional (with defaults)
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Redis (leave empty to disable caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# AI Backend
FLASK_AI_URL=http://localhost:5000

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

## File Permissions (Linux/Mac)

```bash
# Make scripts executable
chmod +x setup.sh
chmod +x backup.sh

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

---

## Development Workflow

### Daily Development
```powershell
# 1. Start services (once)
docker-compose up -d postgres redis

# 2. Start backend (with auto-reload)
uvicorn app.main:app --reload

# 3. Start AI backend (separate terminal)
cd ..\AI
python app.py

# 4. Make changes to code
# Backend reloads automatically

# 5. Run tests
pytest

# 6. Stop services (end of day)
docker-compose stop
```

### Making Database Changes
```powershell
# 1. Modify models in app/models/

# 2. Create migration
alembic revision --autogenerate -m "Add new field"

# 3. Review migration in alembic/versions/

# 4. Apply migration
alembic upgrade head

# 5. Test changes
pytest
```

### Adding New Dependencies
```powershell
# 1. Install package
pip install package-name

# 2. Update requirements
pip freeze > requirements.txt

# 3. Rebuild Docker image
docker-compose build backend
```

---

## Monitoring Commands

### Check System Health
```powershell
# All services status
docker-compose ps

# Resource usage
docker stats

# Backend logs
docker-compose logs -f backend | Select-String "ERROR"

# Database connections
docker-compose exec postgres psql -U dacn_user -d dacn_db -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Metrics
```powershell
# Redis hit rate
docker-compose exec redis redis-cli -a dacn_redis_password INFO stats | Select-String "hit"

# Database size
docker-compose exec postgres psql -U dacn_user -d dacn_db -c "\l+"

# Log errors
docker-compose logs --tail=100 backend | Select-String "ERROR"
```

---

## Additional Resources

### Documentation
- Full setup guide: `SETUP_GUIDE.md`
- Validation guide: `VALIDATION_GUIDE.md`
- Migration guide: `MIGRATION_GUIDE.md`
- Docker guide: `DOCKER_DEPLOYMENT.md`
- Project summary: `PROJECT_SUMMARY.md`

### Online Help
- FastAPI docs: https://fastapi.tiangolo.com/
- Docker docs: https://docs.docker.com/
- Redis docs: https://redis.io/docs/
- PostgreSQL docs: https://www.postgresql.org/docs/

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify services: `docker-compose ps`
3. Test health: `curl http://localhost:8000/health`
4. Review documentation in project root
5. Contact development team

---

## Success Indicators

Your setup is working correctly if:

✅ `docker-compose ps` shows all services as "Up"
✅ http://localhost:8000/docs loads successfully
✅ http://localhost:5000 returns AI backend response
✅ `pytest` passes all tests
✅ No errors in `docker-compose logs`

**Next Steps**: Start developing or deploy to production!
