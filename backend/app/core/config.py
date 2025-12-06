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
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"]
    
    # Preview settings
    DEFAULT_PREVIEW_ROWS: int = 100
    MAX_PREVIEW_ROWS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
