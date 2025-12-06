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
git clone https://github.com/your-org/arc_migrator_tool.git
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

Create a `.env` file in the project root to customize settings:

```env
# Backend Configuration
DATABASE_URL=sqlite+aiosqlite:///./data/arc_migrator.db
UPLOAD_DIR=./data/uploads
OUTPUT_DIR=./data/outputs
DEBUG=false
CORS_ORIGINS=["http://localhost:3000"]
MAX_UPLOAD_SIZE=104857600  # 100MB

# Preview Settings
DEFAULT_PREVIEW_ROWS=100
MAX_PREVIEW_ROWS=1000
```

### Production Configuration

For production deployments, consider:

1. **Use environment-specific configuration**:
```bash
export DATABASE_URL=sqlite+aiosqlite:///./data/production.db
export DEBUG=false
```

2. **Set appropriate CORS origins**:
```bash
export CORS_ORIGINS='["https://your-domain.com"]'
```

3. **Configure file size limits**:
```bash
export MAX_UPLOAD_SIZE=209715200  # 200MB
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

## Uninstallation

### Complete Removal

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Remove images
docker rmi arc_migrator_tool-backend arc_migrator_tool-frontend
```

## Next Steps

After installation, proceed to the [User Guide](USER_GUIDE.md) to learn how to:
- Create migration projects
- Upload and analyze data files
- Configure field mappings
- Execute migrations
