"""
Application configuration and settings.
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Project info
    PROJECT_NAME: str = "ARC Migrator Tool"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://localhost:8080",  # Production frontend
        "http://frontend:5173",   # Docker container
        "http://frontend:80",     # Docker production
    ]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./data/arc_migrator.db"
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    UPLOAD_DIR: str = "./data/uploads"
    EXPORT_DIR: str = "./data/exports"
    
    # Security settings
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # Performance settings
    MAX_PREVIEW_ROWS: int = 1000
    DEFAULT_PREVIEW_ROWS: int = 100
    
    # Cache settings
    ENABLE_CACHING: bool = False
    CACHE_TTL: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
