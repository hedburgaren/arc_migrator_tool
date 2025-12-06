"""
Application configuration and settings.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Project info
    PROJECT_NAME: str = "ARC Migrator Tool"
    VERSION: str = "0.1.0"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://frontend:5173",   # Docker container
    ]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./data/arc_migrator.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
