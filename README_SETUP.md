# ARC Migrator Tool - Setup Guide

This guide explains how to set up and run the ARC Migrator Tool locally using Docker.

## Prerequisites

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Node.js** (version 18 or higher) - for local development
- **Python** (version 3.11 or higher) - for local development

## Quick Start (Production Mode)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arc_migrator_tool
   ```

2. **Build and start the containers**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Mode

For active development with hot reload:

1. **Start the development containers**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Access the application**
   - Frontend (with hot reload): http://localhost:5173
   - Backend API (with auto-reload): http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development Without Docker

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

## Project Structure

```
arc_migrator_tool/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   └── connectors/    # System connectors
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Production compose
├── docker-compose.dev.yml  # Development compose
└── README_SETUP.md         # This file
```

## API Documentation

The backend provides automatic API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Environment Variables

### Backend

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database URL | `sqlite+aiosqlite:///./data/arc_migrator.db` |
| `UPLOAD_DIR` | Directory for uploaded files | `./data/uploads` |
| `OUTPUT_DIR` | Directory for output files | `./data/outputs` |
| `DEBUG` | Enable debug mode | `false` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:5173` |

### Frontend

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL (dev only) | `http://localhost:8000` |

## Using the Application

### 1. Create a Project

1. Click "New Project" on the dashboard
2. Select your source system (e.g., CSV, Zoho CRM)
3. Select your target system (e.g., Odoo, CSV)
4. Give your project a name and description

### 2. Upload Data Files

1. Go to the "Files" tab in your project
2. Drag and drop your CSV or Excel file
3. Click "Upload File"

### 3. Discover Schema

1. After uploading, click "Discover Schema" next to your file
2. The system will automatically analyze your data and detect:
   - Field types (string, number, date, etc.)
   - Required fields
   - Lookup candidates

### 4. Create Mappings

1. Go to the "Mappings" tab
2. Click "New Mapping"
3. Use the visual editor to:
   - Draw connections from source to target fields
   - Add transformations (concat, split, lookup)
   - Configure constant values

### 5. Preview and Execute

1. Click "Preview" to see sample transformations
2. Click "Dry Run" to test without saving
3. Click "Execute" to run the full migration

## Troubleshooting

### Container won't start

Check if ports 3000 or 8000 are already in use:
```bash
lsof -i :3000
lsof -i :8000
```

### Database issues

Reset the database by removing the data volume:
```bash
docker-compose down -v
docker-compose up --build
```

### Frontend build errors

Clear the node modules and rebuild:
```bash
cd frontend
rm -rf node_modules
npm install
```

## Data Persistence

All data is stored in Docker volumes:

- `arc-data`: Contains the SQLite database, uploaded files, and output files

To backup your data:
```bash
docker run --rm -v arc_migrator_tool_arc-data:/data -v $(pwd):/backup alpine tar cvf /backup/arc-data-backup.tar /data
```

To restore:
```bash
docker run --rm -v arc_migrator_tool_arc-data:/data -v $(pwd):/backup alpine tar xvf /backup/arc-data-backup.tar -C /
```

## Support

For issues and feature requests, please open a GitHub issue.
