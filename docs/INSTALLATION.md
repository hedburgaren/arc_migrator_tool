# ARC Migrator Tool - Installation Guide

This guide covers installation and deployment of the ARC Migrator Tool for both development and production environments.

## Prerequisites

### Required Software
- **Docker** (version 20.10 or higher) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 2.0 or higher) - Usually included with Docker Desktop

### Optional (for development)
- **Python 3.11+** - For backend development
- **Node.js 20+** - For frontend development
- **npm 9+** - Package manager for frontend

### System Requirements
- **Minimum**: 2GB RAM, 2 CPU cores, 10GB disk space
- **Recommended**: 4GB RAM, 4 CPU cores, 20GB disk space
- **Operating System**: Linux, macOS, or Windows with WSL2

## Quick Start with Docker

The fastest way to get ARC Migrator running is with Docker Compose.

### 1. Clone the Repository

```bash
git clone https://github.com/hedburgaren/arc_migrator_tool.git
cd arc_migrator_tool
```

### 2. Start the Application

```bash
docker-compose up -d
```

This will:
- Build the backend and frontend containers
- Start the backend API on port 8000
- Start the frontend on port 3000
- Create a persistent volume for data storage

### 3. Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Verify Installation

```bash
# Check container status
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"arc-migrator-backend"}
```

## Development Setup

For development with hot-reload capabilities:

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The development servers will start:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Development Docker Compose

For development with live code mounting:

```bash
docker-compose -f docker-compose.dev.yml up
```

## Configuration

### Environment Variables

Copy the example environment file and customize settings:

```bash
cp .env.example .env
```

Edit `.env` to customize settings:

```env
# Application Environment
ENVIRONMENT=development  # development or production

# Backend Configuration
DATABASE_URL=sqlite:///./data/arc_migrator.db
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Security Settings
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# File Upload Settings
MAX_UPLOAD_SIZE=104857600  # 100 MB in bytes
UPLOAD_DIR=./data/uploads
EXPORT_DIR=./data/exports

# Performance Settings
MAX_PREVIEW_ROWS=1000
DEFAULT_PREVIEW_ROWS=100
ENABLE_CACHING=false
CACHE_TTL=300  # seconds

# Frontend Configuration
VITE_API_URL=http://localhost:8000
NODE_ENV=development
```

### Production Configuration

For production deployments:

1. **Use production environment**:
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
NODE_ENV=production
```

2. **Set appropriate CORS origins**:
Add your domain to ALLOWED_ORIGINS in `backend/app/core/config.py`

3. **Enable security features**:
```bash
RATE_LIMIT_PER_MINUTE=30  # Lower for production
RATE_LIMIT_PER_HOUR=500
```

4. **Optimize performance**:
```bash
ENABLE_CACHING=true
MAX_UPLOAD_SIZE=209715200  # 200MB
```

5. **Use production Docker Compose**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Data Persistence

### Docker Volumes

Data is persisted in Docker volumes:
- `arc-data`: Contains database and uploaded files

To backup your data:
```bash
docker run --rm -v arc-data:/data -v $(pwd):/backup alpine tar cvf /backup/arc-backup.tar /data
```

To restore data:
```bash
docker run --rm -v arc-data:/data -v $(pwd):/backup alpine tar xvf /backup/arc-backup.tar -C /
```

### Local Development

In development mode, data is stored in:
- `backend/data/arc_migrator.db` - SQLite database
- `backend/data/uploads/` - Uploaded files
- `backend/data/outputs/` - Generated output files

## Troubleshooting

### Common Issues

#### Port Conflicts
If ports 3000 or 8000 are in use:
```bash
# Change ports in docker-compose.yml
ports:
  - "3001:80"  # Frontend
  - "8001:8000"  # Backend
```

#### Permission Issues on Linux
```bash
# Fix Docker volume permissions
sudo chown -R $USER:$USER ./backend/data
```

#### Container Fails to Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Database Issues
```bash
# Reset database (WARNING: This deletes all data)
docker-compose down -v
docker-compose up -d
```

### Health Checks

Both services include health checks:
- Backend: `GET /health`
- Frontend: Static file check via nginx

Monitor health status:
```bash
docker inspect arc-migrator-backend --format='{{.State.Health.Status}}'
docker inspect arc-migrator-frontend --format='{{.State.Health.Status}}'
```

## Upgrading

### Standard Upgrade

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d
```

### Preserve Data During Upgrade

Docker volumes are preserved by default. To ensure data safety:
1. Backup your data (see Data Persistence section)
2. Perform the upgrade
3. Verify the application works
4. Delete the backup only after confirming everything is functional

## Production Deployment

### Production Docker Deployment

For production, use the optimized Docker Compose configuration:

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env and set ENVIRONMENT=production

# Start with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Production Features

The production setup includes:

- **Multi-stage Docker builds** - Optimized image sizes
- **Nginx frontend** - Efficient static file serving with caching
- **Security headers** - CSP, XSS protection, frame options
- **Rate limiting** - Protection against abuse
- **Structured logging** - JSON logs for monitoring
- **Health checks** - Automatic container health monitoring
- **Multiple workers** - 4 Uvicorn workers for backend

### Security Best Practices

1. **Change default settings**:
   - Update rate limits based on your needs
   - Configure appropriate CORS origins
   - Review and adjust security headers

2. **File upload security**:
   - Files are validated by type and size
   - Magic number verification prevents fake files
   - Filenames are sanitized to prevent path traversal

3. **Monitoring and logging**:
   - Check logs in `backend/data/logs/`
   - Monitor metrics at `/metrics` endpoint
   - Review audit logs for user actions

4. **Regular updates**:
   ```bash
   git pull origin main
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Performance Tuning

1. **Database optimization**:
   - Consider PostgreSQL for production (update DATABASE_URL)
   - Regular backups recommended

2. **Caching**:
   ```bash
   ENABLE_CACHING=true
   CACHE_TTL=300
   ```

3. **File size limits**:
   ```bash
   MAX_UPLOAD_SIZE=209715200  # 200MB
   ```

4. **Preview limits**:
   ```bash
   MAX_PREVIEW_ROWS=1000
   DEFAULT_PREVIEW_ROWS=100
   ```

### Monitoring

Access monitoring endpoints:

- **Health check**: `curl http://localhost:8000/health`
- **Metrics**: `curl http://localhost:8000/metrics`

Example metrics response:
```json
{
  "durations": {
    "file_upload": {"avg": 245.5, "p95": 450.2, "p99": 890.1},
    "schema_analysis": {"avg": 125.3, "p95": 280.5, "p99": 520.8}
  },
  "counters": {
    "files_uploaded": 142,
    "mappings_created": 58,
    "executions_completed": 23
  }
}
```

## Backup and Recovery

### Backup Data

```bash
# Create backup directory
mkdir -p backups

# Backup Docker volume
docker run --rm \
  -v arc-migrator-backend-prod_backend-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/arc-data-$(date +%Y%m%d).tar.gz /data

# Or for development
cp -r backend/data backups/data-$(date +%Y%m%d)
```

### Restore Data

```bash
# Restore Docker volume
docker run --rm \
  -v arc-migrator-backend-prod_backend-data:/data \
  -v $(pwd)/backups:/backup \
  alpine sh -c "cd / && tar xzf /backup/arc-data-YYYYMMDD.tar.gz"

# Or for development
cp -r backups/data-YYYYMMDD backend/data
```

## Uninstallation

### Complete Removal

```bash
# Stop and remove containers
docker-compose down
# Or for production
docker-compose -f docker-compose.prod.yml down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Remove images
docker rmi arc_migrator_tool-backend arc_migrator_tool-frontend
```

## Next Steps

After installation, proceed to the [User Guide](USER_GUIDE.md) to learn how to:
- Create migration projects
- Upload and analyze data files
- Use Excel multi-sheet support
- Create field mappings with transform nodes
- Execute and monitor migrations
