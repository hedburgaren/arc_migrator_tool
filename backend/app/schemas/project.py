"""
Pydantic schemas for project operations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base schema for project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    source_system: Optional[str] = Field(None, max_length=100)
    target_system: Optional[str] = Field(None, max_length=100)
    status: str = Field(default="draft", max_length=50)


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    source_system: Optional[str] = Field(None, max_length=100)
    target_system: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=50)


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
