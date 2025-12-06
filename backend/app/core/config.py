"""Application configuration settings."""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "ARC Migrator Tool"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/arc_migrator.db"
    
    # File storage
    UPLOAD_DIR: str = "./data/uploads"
    OUTPUT_DIR: str = "./data/outputs"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # CORS - Default to empty list for production security
    # Set via environment variable: CORS_ORIGINS='["http://localhost:3000"]'
    # In Docker, frontend requests are proxied through nginx, so CORS isn't needed
    CORS_ORIGINS: List[str] = []
    
    # Preview settings
    DEFAULT_PREVIEW_ROWS: int = 100
    MAX_PREVIEW_ROWS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
