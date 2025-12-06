"""
Main FastAPI application entry point for ARC Migrator Tool.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, files, schemas, projects, mappings, executions, transform, exports, validation
from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import setup_logging
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ARC Migrator Tool - Visual data migration framework"
)

# Add security middleware
# Note: Middleware is applied in reverse order (last added = first executed)

# Security headers (applied last, to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting (applied before security headers)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
    requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
)

# Configure CORS (applied first)
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
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(mappings.router, prefix="/api", tags=["mappings"])
app.include_router(executions.router, prefix="/api", tags=["executions"])
app.include_router(transform.router, prefix="/api", tags=["transform"])
app.include_router(exports.router, prefix="/api", tags=["exports"])
app.include_router(validation.router, prefix="/api", tags=["validation"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and logging on startup."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    init_db()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Application shutting down")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ARC Migrator Tool API",
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    from app.core.logging_config import get_metrics_collector
    
    metrics_collector = get_metrics_collector()
    return metrics_collector.get_all_metrics()
