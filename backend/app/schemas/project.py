"""
Pydantic schemas for project operations.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base schema for project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    source_system: Optional[str] = Field(None, max_length=100)
    target_system: Optional[str] = Field(None, max_length=100)
    status: Literal["draft", "active", "completed", "archived"] = Field(default="draft")


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    source_system: Optional[str] = Field(None, max_length=100)
    target_system: Optional[str] = Field(None, max_length=100)
    status: Optional[Literal["draft", "active", "completed", "archived"]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    validation_status: str = Field(default="pending")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
