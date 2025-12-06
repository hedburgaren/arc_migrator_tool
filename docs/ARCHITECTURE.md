# ARC Migrator Tool - Architecture Guide

This document provides a comprehensive overview of the ARC Migrator Tool architecture, including system design, data flow, and extension points.

## System Overview

ARC Migrator Tool is a full-stack application designed for visual data migration. It follows a modern microservices-ready architecture with a clear separation between frontend and backend components.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │   Dashboard  │   Project    │   Mapping    │  Execution   │  │
│  │              │   Wizard     │   Editor     │   Monitor    │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                    React + ReactFlow + TailwindCSS              │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP/REST API
┌────────────────────────────────┴────────────────────────────────┐
│                          Backend API                            │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │   Projects   │    Files     │   Schemas    │  Executions  │  │
│  │   Endpoint   │   Endpoint   │   Endpoint   │   Endpoint   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                         FastAPI + Pydantic                      │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                        Service Layer                            │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │    File      │   Schema     │   Mapping    │  Execution   │  │
│  │   Parser     │  Discovery   │   Engine     │   Engine     │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                      Pandas + Business Logic                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────┐
│                        Data Layer                               │
│  ┌─────────────────────────────┐  ┌──────────────────────────┐  │
│  │      SQLite Database        │  │      File Storage        │  │
│  │  (Projects, Schemas, etc.)  │  │   (Uploads, Outputs)     │  │
│  └─────────────────────────────┘  └──────────────────────────┘  │
│                       SQLAlchemy + Async IO                     │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **ReactFlow** - Visual node-based editor
- **TailwindCSS** - Utility-first CSS
- **Tanstack Query** - Server state management
- **Axios** - HTTP client
- **Zustand** - Client state management
- **React Router** - Navigation
- **Lucide React** - Icon library

### Backend
- **Python 3.11** - Programming language
- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - ORM with async support
- **Pydantic v2** - Data validation
- **Pandas** - Data manipulation
- **aiosqlite** - Async SQLite driver
- **chardet** - Encoding detection
- **openpyxl** - Excel file support

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **nginx** - Frontend static file server and reverse proxy
- **SQLite** - Database (single-file, no external dependencies)

## Component Architecture

### Frontend Components

```
src/
├── App.tsx              # Main app with routing
├── main.tsx             # Entry point
├── index.css            # Global styles
├── components/          # Reusable UI components
│   ├── Layout.tsx       # App shell with navigation
│   ├── FileUpload.tsx   # Drag-and-drop file upload
│   ├── MappingEditor.tsx # ReactFlow-based visual editor
│   ├── PreviewDashboard.tsx # Data comparison view
│   └── SchemaView.tsx   # Schema field list
├── pages/               # Route-based pages
│   ├── Dashboard.tsx    # Project list
│   ├── ProjectWizard.tsx # New project creation
│   ├── ProjectDetail.tsx # Project management
│   ├── MappingWorkspace.tsx # Mapping configuration
│   └── ExecutionMonitor.tsx # Execution tracking
├── services/
│   └── api.ts           # Type-safe API client
└── types/
    └── index.ts         # TypeScript interfaces
```

### Backend Components

```
app/
├── main.py              # FastAPI application entry
├── core/                # Core infrastructure
│   ├── config.py        # Settings management
│   └── database.py      # Database configuration
├── api/                 # REST endpoints
│   ├── health.py        # Health checks
│   ├── projects.py      # Project CRUD
│   ├── files.py         # File upload/management
│   ├── schemas.py       # Schema discovery
│   ├── mappings.py      # Mapping configuration
│   └── executions.py    # Migration execution
├── models/              # SQLAlchemy models
│   ├── project.py       # Migration project
│   ├── file.py          # Source file metadata
│   ├── schema.py        # Schema definitions
│   ├── mapping.py       # Mapping profiles
│   └── execution.py     # Execution history
├── services/            # Business logic
│   ├── file_parser.py   # File parsing service
│   ├── schema_discovery.py # Schema analysis
│   ├── mapping_engine.py # Transform execution
│   ├── execution_engine.py # Migration pipeline
│   └── validation_service.py # Data validation
└── connectors/          # System connectors
    └── base.py          # Connector interface
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐
│     Project     │────<│   SourceFile    │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │
│ name            │     │ project_id (FK) │
│ description     │     │ filename        │
│ source_system   │     │ file_path       │
│ target_system   │     │ file_type       │
│ status          │     │ encoding        │
│ created_at      │     │ row_count       │
│ updated_at      │     │ column_count    │
└─────────────────┘     └─────────────────┘
        │                       │
        │     ┌─────────────────┴───────────────┐
        │     │                                 │
        v     v                                 v
┌─────────────────┐                   ┌─────────────────┐
│ SchemaDefinition│                   │ FieldDefinition │
├─────────────────┤                   ├─────────────────┤
│ id              │──────────────────<│ id              │
│ project_id (FK) │                   │ schema_id (FK)  │
│ file_id (FK)    │                   │ name            │
│ name            │                   │ field_type      │
│ schema_type     │                   │ is_required     │
│ system_type     │                   │ is_primary_key  │
└─────────────────┘                   │ is_lookup       │
        │                             │ sample_values   │
        │                             └─────────────────┘
        v
┌─────────────────┐     ┌─────────────────┐
│ MappingProfile  │────<│  MappingEdge    │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │
│ project_id (FK) │     │ profile_id (FK) │
│ name            │     │ source_field_id │
│ source_schema_id│     │ target_field_id │
│ target_schema_id│     │ mapping_type    │
│ version         │     │ transform_type  │
│ layout_json     │     │ transform_config│
└─────────────────┘     │ lookup_table    │
        │               └─────────────────┘
        v
┌─────────────────┐     ┌─────────────────┐
│  ExecutionRun   │────<│  ExecutionLog   │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │
│ project_id (FK) │     │ execution_id(FK)│
│ profile_id (FK) │     │ level           │
│ mode            │     │ message         │
│ status          │     │ record_index    │
│ total_records   │     │ field_name      │
│ output_files    │     │ timestamp       │
└─────────────────┘     └─────────────────┘
```

### Status Enumerations

**ProjectStatus**
- `draft` - Initial state
- `mapping` - Configuration in progress
- `ready` - Ready for execution
- `executing` - Migration running
- `completed` - Successfully finished
- `failed` - Error occurred

**ExecutionMode**
- `preview` - Sample data only (no output)
- `dry_run` - Full validation (no output)
- `commit` - Full execution with output files

**ExecutionStatus**
- `pending` - Not yet started
- `running` - In progress
- `completed` - Finished successfully
- `failed` - Error occurred
- `cancelled` - User cancelled

## Data Flow

### File Upload Flow

```
User uploads file → FileUpload.tsx
                        │
                        ▼
         POST /api/files/upload/{project_id}
                        │
                        ▼
              files.py endpoint
                        │
                        ├─► Validate file type/size
                        │
                        ├─► Save file to storage
                        │
                        ├─► Parse with FileParser
                        │   ├─► Detect encoding
                        │   ├─► Parse CSV/Excel/JSON
                        │   └─► Extract metadata
                        │
                        └─► Create SourceFile record
                                    │
                                    ▼
                          Return file metadata
```

### Schema Discovery Flow

```
User clicks "Discover Schema"
                │
                ▼
      POST /api/schemas/discover
                │
                ▼
        schemas.py endpoint
                │
                ├─► Load file with FileParser
                │
                ├─► Analyze with SchemaDiscoveryService
                │   ├─► Infer field types
                │   ├─► Detect lookup candidates
                │   ├─► Identify primary keys
                │   └─► Extract sample values
                │
                └─► Create SchemaDefinition + FieldDefinitions
                            │
                            ▼
                  Return schema with fields
```

### Mapping Execution Flow

```
User clicks "Execute"
        │
        ▼
POST /api/executions/execute
        │
        ▼
  executions.py endpoint
        │
        ├─► Load mapping profile and edges
        │
        ├─► Parse source file
        │
        ├─► Build edge configurations
        │
        ├─► Create ExecutionRun record
        │
        ├─► Execute with ExecutionEngine
        │   │
        │   ├─► Apply mappings (MappingEngine)
        │   │   ├─► Process each row
        │   │   ├─► Apply transforms
        │   │   └─► Track warnings
        │   │
        │   ├─► Validate results (ValidationService)
        │   │
        │   └─► Generate output files (commit mode)
        │
        └─► Save execution results and logs
                    │
                    ▼
            Return execution result
```

## Service Details

### FileParser Service

Handles file I/O with automatic format detection:

```python
class FileParser:
    def parse_file(file_path, file_type, **kwargs):
        # Auto-detect encoding for CSV
        # Support multiple delimiters (comma, semicolon, tab)
        # Handle Excel with multiple sheets
        # Return DataFrame + metadata
```

**Features:**
- Encoding detection with chardet
- Multi-delimiter support for CSV
- Excel sheet selection
- JSON (array and line-delimited)
- Metadata extraction (row count, columns, etc.)

### SchemaDiscoveryService

Analyzes data structure and characteristics:

```python
class SchemaDiscoveryService:
    def discover_schema(df, schema_name):
        # Analyze each column
        # Infer data types
        # Detect lookup candidates
        # Identify primary keys
        # Extract sample values
```

**Type Inference:**
- String pattern matching
- Numeric detection
- Date/datetime parsing
- Boolean value recognition
- Enum/lookup detection

### MappingEngine

Applies field transformations:

```python
class MappingEngine:
    def apply_mappings(source_df, edges, target_fields):
        # For each row:
        #   For each mapping edge:
        #     Apply transform
        #     Track warnings
        # Return transformed DataFrame
```

**Transform Types:**
- Direct copy
- Text transforms (upper, lower, trim)
- String operations (concat, split, replace)
- Type conversions (to_number, to_string)
- Date formatting
- Lookup/value mapping

### ExecutionEngine

Orchestrates the migration pipeline:

```python
class ExecutionEngine:
    async def execute(source_df, edges, target_fields, mode, ...):
        # Apply mappings
        # Validate results
        # Generate output (commit mode)
        # Track logs and statistics
        # Return execution result
```

**Execution Modes:**
- Preview: First 100 rows, no output
- Dry Run: All rows, validation only
- Commit: All rows, generate files

### ValidationService

Validates data against rules:

```python
class ValidationService:
    def validate_dataframe(df, field_defs, rules):
        # Check required fields
        # Validate data types
        # Apply custom rules (pattern, length, range)
        # Return validation errors
```

## Connector Framework

### Base Interface

All connectors implement `ConnectorBase`:

```python
class ConnectorBase(ABC):
    async def connect() -> bool
    async def disconnect() -> None
    async def get_schema(model_name) -> Dict
    async def extract(model_name, filters, limit) -> DataFrame
    async def push(model_name, data, mode) -> Dict
```

### Connector Registry

Connectors are discovered and managed by `ConnectorRegistry`:

```python
ConnectorRegistry.register(CSVConnector)
ConnectorRegistry.list_all()  # Available connectors
ConnectorRegistry.create("csv", config)  # Instantiate
```

### Built-in Connectors

**CSVConnector**
- Read/write CSV files
- Handles encoding and delimiters
- Integrates with FileParser

### Adding Custom Connectors

1. Create a new file in `connectors/`:

```python
# connectors/zoho_connector.py
from app.connectors.base import ConnectorBase, ConnectorRegistry

class ZohoConnector(ConnectorBase):
    name = "zoho"
    display_name = "Zoho CRM"
    
    async def connect(self):
        # Connect to Zoho API
        pass
    
    async def get_schema(self, model_name=None):
        # Fetch module/field definitions
        pass
    
    async def extract(self, model_name, filters=None, limit=None):
        # Extract records from Zoho
        pass
    
    async def push(self, model_name, data, mode="create"):
        # Push records to Zoho
        pass

ConnectorRegistry.register(ZohoConnector)
```

2. Import in `connectors/__init__.py`

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/projects` | GET | List projects |
| `/api/projects` | POST | Create project |
| `/api/projects/{id}` | GET | Get project |
| `/api/projects/{id}` | PUT | Update project |
| `/api/projects/{id}` | DELETE | Delete project |
| `/api/files/upload/{project_id}` | POST | Upload file |
| `/api/files/project/{project_id}` | GET | List project files |
| `/api/files/{id}/preview` | GET | Get file preview |
| `/api/schemas/discover` | POST | Discover schema |
| `/api/schemas/project/{project_id}` | GET | List schemas |
| `/api/schemas/{id}` | GET | Get schema with fields |
| `/api/mappings/project/{project_id}` | POST | Create mapping |
| `/api/mappings/{id}` | GET | Get mapping with edges |
| `/api/mappings/{id}/edges` | POST | Add edge |
| `/api/mappings/{id}/preview` | POST | Preview mapping |
| `/api/executions/execute` | POST | Run migration |
| `/api/executions/{id}` | GET | Get execution details |

### OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Security Considerations

### Input Validation
- File type validation (allowed extensions only)
- File size limits (configurable, default 100MB)
- Pydantic models validate all API inputs
- SQL injection prevention via SQLAlchemy ORM

### File Handling
- Unique filenames prevent path traversal
- Files stored in dedicated directory
- Non-root user in Docker containers

### CORS Configuration
- Configurable allowed origins
- Default: empty (Docker proxy handles requests)
- Development: localhost origins

### Error Handling
- Generic error messages in production
- Detailed logs for debugging
- No stack traces exposed in API responses

## Performance Considerations

### File Processing
- Streaming file uploads
- Chunk-based CSV processing for large files
- Memory-efficient DataFrame operations

### Database
- Async SQLite with aiosqlite
- Connection pooling via SQLAlchemy
- Indexed foreign keys

### Frontend
- React Query caching
- Pagination for large lists
- Lazy loading for components

## Deployment Options

### Single Docker Host
```bash
docker-compose up -d
```

### Kubernetes
The application can be adapted for K8s deployment:
- Backend: Deployment with ReplicaSet
- Frontend: Deployment with nginx
- Database: PersistentVolumeClaim for SQLite
- Ingress: Route traffic to services

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Configure CORS origins
- [ ] Set up volume backups
- [ ] Configure resource limits
- [ ] Enable logging aggregation
- [ ] Set up health check monitoring
