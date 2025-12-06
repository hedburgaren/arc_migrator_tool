# Production Deployment Guide

This guide provides detailed instructions for deploying ARC Migrator Tool in a production environment.

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] Docker and Docker Compose installed (v20.10+ and v2.0+)
- [ ] Minimum 4GB RAM, 4 CPU cores
- [ ] 20GB+ available disk space
- [ ] Network access for API communication
- [ ] HTTPS/SSL certificates (recommended)
- [ ] Backup strategy in place

### Security Review

- [ ] Review and update `.env` configuration
- [ ] Configure appropriate rate limits
- [ ] Set production CORS origins
- [ ] Review security headers
- [ ] Enable HTTPS (recommended)
- [ ] Set up monitoring and alerting

## Deployment Steps

### 1. Prepare Environment

```bash
# Clone repository
git clone https://github.com/hedburgaren/arc_migrator_tool.git
cd arc_migrator_tool

# Create production environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file:

```env
# Production configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
NODE_ENV=production

# Security
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500

# Performance
ENABLE_CACHING=true
MAX_UPLOAD_SIZE=209715200  # 200MB

# Database (optional: switch to PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost:5432/arc_migrator
```

### 3. Build and Start Services

```bash
# Build and start in production mode
docker-compose -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"arc-migrator-backend"}

# Check frontend
curl http://localhost/health
# Expected: healthy

# Check metrics
curl http://localhost:8000/metrics
```

## Production Configuration

### Security Headers

The production setup includes comprehensive security headers:

- **Content Security Policy (CSP)**: Prevents XSS attacks
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME sniffing
- **X-XSS-Protection**: Browser XSS protection
- **Referrer-Policy**: Controls referrer information
- **Permissions-Policy**: Restricts browser features

### Rate Limiting

Default rate limits:
- 30 requests per minute per IP
- 500 requests per hour per IP

Customize in `.env`:
```env
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500
```

### Logging

Production logging features:
- **Structured JSON logs**: Easy to parse and analyze
- **Log rotation**: Automatic rotation at 10MB, keeps 5 backups
- **Error logs**: Separate error log file
- **Audit logs**: Track user actions for compliance

Log locations:
```
backend/data/logs/
├── arc_migrator.log       # Application logs
├── arc_migrator_errors.log # Error logs only
└── audit.log              # Audit trail
```

### Monitoring

#### Health Checks

- **Backend**: `GET /health`
- **Frontend**: `GET /health`
- **Metrics**: `GET /metrics`

#### Metrics Endpoint

Access detailed performance metrics:

```bash
curl http://localhost:8000/metrics
```

Example response:
```json
{
  "durations": {
    "file_upload": {
      "count": 142,
      "min": 45.2,
      "max": 1205.8,
      "avg": 245.5,
      "p50": 198.3,
      "p95": 450.2,
      "p99": 890.1
    },
    "schema_analysis": {
      "count": 142,
      "avg": 125.3,
      "p95": 280.5
    }
  },
  "counters": {
    "files_uploaded": 142,
    "mappings_created": 58,
    "executions_completed": 23
  }
}
```

#### Container Health Checks

Docker automatically monitors container health:

```bash
# Check health status
docker inspect arc-migrator-backend-prod --format='{{.State.Health.Status}}'
docker inspect arc-migrator-frontend-prod --format='{{.State.Health.Status}}'
```

### Performance Optimization

#### Caching

Enable caching for improved performance:

```env
ENABLE_CACHING=true
CACHE_TTL=300  # 5 minutes
```

#### Database Optimization

For high-volume production use, consider PostgreSQL:

1. **Install PostgreSQL**:
```bash
docker run -d \
  --name arc-postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=arc_migrator \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:15
```

2. **Update DATABASE_URL**:
```env
DATABASE_URL=postgresql://postgres:yourpassword@arc-postgres:5432/arc_migrator
```

3. **Add indexes** (recommended):
```sql
CREATE INDEX idx_files_upload_date ON files(upload_timestamp);
CREATE INDEX idx_mappings_project ON mappings(project_id);
CREATE INDEX idx_executions_status ON executions(status, start_time);
```

#### Frontend Optimization

The production frontend includes:
- **Nginx**: High-performance web server
- **Static asset caching**: 1-year cache for JS/CSS/images
- **Gzip compression**: Reduces bandwidth usage
- **Security headers**: Enhanced protection

## Backup and Recovery

### Automated Backup Script

Create `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Docker volume
docker run --rm \
  -v arc-migrator-backend-prod_backend-data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/arc-data-${DATE}.tar.gz /data

# Cleanup old backups (keep last 7 days)
find ${BACKUP_DIR} -name "arc-data-*.tar.gz" -mtime +7 -delete

echo "Backup completed: arc-data-${DATE}.tar.gz"
```

### Scheduled Backups

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/arc-backup.log 2>&1
```

### Recovery Procedure

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore data
docker run --rm \
  -v arc-migrator-backend-prod_backend-data:/data \
  -v /path/to/backups:/backup \
  alpine sh -c "cd / && tar xzf /backup/arc-data-YYYYMMDD_HHMMSS.tar.gz"

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

## Maintenance

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose -f docker-compose.prod.yml build

# Restart with zero downtime
docker-compose -f docker-compose.prod.yml up -d
```

### Log Rotation

Logs rotate automatically at 10MB. Manual cleanup:

```bash
# Compress old logs
find backend/data/logs -name "*.log.*" -exec gzip {} \;

# Archive logs older than 30 days
find backend/data/logs -name "*.log.*.gz" -mtime +30 -exec mv {} /archive/ \;
```

### Resource Monitoring

Monitor resource usage:

```bash
# Check container stats
docker stats

# Check disk usage
du -sh backend/data/*

# Check logs size
du -sh backend/data/logs
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Rebuild from scratch
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Restart services to free memory
docker-compose -f docker-compose.prod.yml restart

# Increase Docker memory limits if needed
```

### Database Issues

```bash
# Backup current database
cp backend/data/arc_migrator.db backend/data/arc_migrator.db.backup

# Check database integrity
sqlite3 backend/data/arc_migrator.db "PRAGMA integrity_check;"

# Vacuum database to reclaim space
sqlite3 backend/data/arc_migrator.db "VACUUM;"
```

### Performance Issues

1. **Enable caching**:
```env
ENABLE_CACHING=true
```

2. **Increase rate limits** if legitimate traffic is being blocked:
```env
RATE_LIMIT_PER_MINUTE=60
```

3. **Monitor metrics**:
```bash
watch -n 5 curl -s http://localhost:8000/metrics
```

4. **Check resource usage**:
```bash
docker stats
```

## Security Best Practices

1. **Regular updates**: Keep Docker, OS, and application up to date
2. **Firewall**: Restrict access to necessary ports only
3. **HTTPS**: Use reverse proxy (nginx/traefik) with SSL certificates
4. **Monitoring**: Set up alerting for unusual activity
5. **Backups**: Test recovery procedures regularly
6. **Audit logs**: Review regularly for suspicious activity
7. **Rate limiting**: Adjust based on legitimate traffic patterns
8. **File uploads**: Monitor for malicious files

## Support and Documentation

- **Installation Guide**: [INSTALLATION.md](docs/INSTALLATION.md)
- **User Guide**: [USER_GUIDE.md](docs/USER_GUIDE.md)
- **Architecture**: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Documentation**: http://localhost:8000/docs
