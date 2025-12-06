"""
Main FastAPI application entry point for ARC Migrator Tool.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, files, schemas
from app.core.config import settings
from app.core.database import init_db

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ARC Migrator Tool - Convert ARC to RO-Crate format"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(schemas.router, prefix="/api/files", tags=["schemas"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ARC Migrator Tool API",
        "version": settings.VERSION,
        "status": "running"
    }
