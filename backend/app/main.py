"""ARC Migrator Tool - FastAPI Backend Application."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import projects, files, schemas, mappings, executions, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting ARC Migrator Tool backend...")
    
    # Ensure data directories exist
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ARC Migrator Tool backend...")


app = FastAPI(
    title="ARC Migrator Tool",
    description="A visual data migration framework for moving business-critical data between ERP, CRM and e-commerce systems",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(schemas.router, prefix="/api/schemas", tags=["Schemas"])
app.include_router(mappings.router, prefix="/api/mappings", tags=["Mappings"])
app.include_router(executions.router, prefix="/api/executions", tags=["Executions"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ARC Migrator Tool",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
