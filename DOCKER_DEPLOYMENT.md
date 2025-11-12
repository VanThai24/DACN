# Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- 10GB free disk space

### Start All Services
```bash
cd backend_src
docker-compose up -d
```

That's it! All services are now running:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- AI Backend: http://localhost:5000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Detailed Setup

### 1. Environment Configuration

**Create `.env` file:**
```bash
cd backend_src
cp .env.example .env
```

**Edit `.env` for production:**
```bash
# Database (will be created automatically)
DATABASE_URL=postgresql://dacn_user:dacn_password@postgres:5432/dacn_db

# Redis (configure password)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=change-this-password

# Security (CRITICAL: change in production)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Environment
ENVIRONMENT=production

# CORS (update with your domains)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 2. Build and Start Services

**Build images:**
```bash
docker-compose build
```

**Start in background:**
```bash
docker-compose up -d
```

**Start with logs:**
```bash
docker-compose up
```

**Start specific service:**
```bash
docker-compose up -d backend
```

### 3. Initialize Database

**Run migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

**Seed initial data (optional):**
```bash
docker-compose exec backend python -m app.seed
```

### 4. Verify Deployment

**Check service status:**
```bash
docker-compose ps
```

Expected output:
```
NAME              IMAGE            STATUS        PORTS
dacn_backend      backend:latest   Up 2 minutes  0.0.0.0:8000->8000/tcp
dacn_postgres     postgres:15      Up 2 minutes  0.0.0.0:5432->5432/tcp
dacn_redis        redis:7          Up 2 minutes  0.0.0.0:6379->6379/tcp
dacn_ai_backend   ai_backend:latest Up 2 minutes 0.0.0.0:5000->5000/tcp
```

**Check logs:**
```bash
docker-compose logs -f
```

**Test API:**
```bash
curl http://localhost:8000/docs
curl http://localhost:8000/health
```

---

## Service Management

### View Logs

**All services:**
```bash
docker-compose logs -f
```

**Specific service:**
```bash
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

**Last 100 lines:**
```bash
docker-compose logs --tail=100 backend
```

### Restart Services

**Restart all:**
```bash
docker-compose restart
```

**Restart specific service:**
```bash
docker-compose restart backend
```

### Stop Services

**Stop all (containers remain):**
```bash
docker-compose stop
```

**Stop and remove containers:**
```bash
docker-compose down
```

**Stop and remove everything (including volumes):**
```bash
docker-compose down -v
```

### Scale Services

**Run multiple backend instances:**
```bash
docker-compose up -d --scale backend=3
```

### Execute Commands in Containers

**Open shell in backend:**
```bash
docker-compose exec backend bash
```

**Run Python command:**
```bash
docker-compose exec backend python -c "print('Hello')"
```

**Run alembic:**
```bash
docker-compose exec backend alembic current
```

**Access PostgreSQL:**
```bash
docker-compose exec postgres psql -U dacn_user -d dacn_db
```

**Access Redis CLI:**
```bash
docker-compose exec redis redis-cli -a dacn_redis_password
```

---

## Maintenance

### Backup Database

**PostgreSQL backup:**
```bash
docker-compose exec -T postgres pg_dump -U dacn_user dacn_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restore from backup:**
```bash
cat backup.sql | docker-compose exec -T postgres psql -U dacn_user -d dacn_db
```

### View Database Size
```bash
docker-compose exec postgres psql -U dacn_user -d dacn_db -c "\l+"
```

### Clear Redis Cache
```bash
docker-compose exec redis redis-cli -a dacn_redis_password FLUSHDB
```

### View Redis Stats
```bash
docker-compose exec redis redis-cli -a dacn_redis_password INFO stats
```

### Clean Up Docker

**Remove unused images:**
```bash
docker image prune -a
```

**Remove unused volumes:**
```bash
docker volume prune
```

**Full cleanup:**
```bash
docker system prune -a --volumes
```

---

## Monitoring

### Resource Usage

**View container stats:**
```bash
docker stats
```

**View specific service:**
```bash
docker stats dacn_backend
```

### Health Checks

**Backend health:**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

**Check container health:**
```bash
docker inspect --format='{{.State.Health.Status}}' dacn_backend
```

### Log Analysis

**Search logs:**
```bash
docker-compose logs | grep ERROR
docker-compose logs backend | grep -i "cache hit"
```

**Export logs:**
```bash
docker-compose logs > logs_$(date +%Y%m%d).txt
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs backend
```

**Check dependencies:**
```bash
docker-compose ps
```

**Restart with rebuild:**
```bash
docker-compose down
docker-compose up -d --build
```

### Database Connection Error

**Check PostgreSQL is running:**
```bash
docker-compose ps postgres
```

**Check database logs:**
```bash
docker-compose logs postgres
```

**Verify connection:**
```bash
docker-compose exec backend python -c "
from app.database import engine
try:
    engine.connect()
    print('✅ Database connected')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Redis Connection Error

**Check Redis is running:**
```bash
docker-compose ps redis
```

**Test connection:**
```bash
docker-compose exec redis redis-cli -a dacn_redis_password ping
```

Expected: `PONG`

### Port Already in Use

**Find process using port:**
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

**Change port in docker-compose.yml:**
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Map to different host port
```

### Out of Disk Space

**Check disk usage:**
```bash
docker system df
```

**Clean up:**
```bash
docker system prune -a --volumes
```

### Performance Issues

**Increase memory limits in docker-compose.yml:**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

**Check container resources:**
```bash
docker stats
```

---

## Production Deployment

### Security Checklist

- [ ] Change all default passwords
- [ ] Generate secure JWT_SECRET_KEY
- [ ] Update CORS_ORIGINS with actual domains
- [ ] Enable Redis password authentication
- [ ] Use HTTPS with reverse proxy
- [ ] Restrict PostgreSQL access
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerts
- [ ] Enable Docker log rotation
- [ ] Regular security updates

### Reverse Proxy Setup (Nginx)

**nginx.conf example:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/TLS Setup

**Using Let's Encrypt:**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Environment Variables for Production

```bash
# .env.production
DATABASE_URL=postgresql://dacn_user:$(openssl rand -base64 32)@postgres:5432/dacn_db
REDIS_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -hex 64)
ENVIRONMENT=production
CORS_ORIGINS=https://app.yourdomain.com
LOG_LEVEL=WARNING
```

### Backup Strategy

**Automated daily backups:**
```bash
# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups

# Backup database
docker-compose exec -T postgres pg_dump -U dacn_user dacn_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup volumes
docker run --rm -v dacn_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres_volume_$DATE.tar.gz -C /data .
docker run --rm -v dacn_redis_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/redis_volume_$DATE.tar.gz -C /data .

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Cron job:**
```bash
# Add to crontab
0 2 * * * /path/to/backup.sh >> /var/log/dacn_backup.log 2>&1
```

### Update Procedure

**Zero-downtime update:**
```bash
# 1. Pull latest code
git pull origin main

# 2. Build new images
docker-compose build

# 3. Run migrations (if any)
docker-compose exec backend alembic upgrade head

# 4. Graceful restart
docker-compose up -d --no-deps --build backend

# 5. Verify
docker-compose ps
docker-compose logs -f backend
```

### Monitoring Setup

**Add monitoring service to docker-compose.yml:**
```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
```

---

## Docker Compose Reference

### Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# Remove services
docker-compose down

# View logs
docker-compose logs -f

# Execute command
docker-compose exec <service> <command>

# Scale service
docker-compose up -d --scale backend=3

# Rebuild images
docker-compose build

# Pull latest images
docker-compose pull

# View configuration
docker-compose config

# List containers
docker-compose ps
```

### Service Configuration

**Override for production:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

**Use override:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)

---

## Support

For deployment issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test health endpoints
4. Review this guide
5. Contact DevOps team
