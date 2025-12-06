"""
Pydantic schemas for export operations.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ExportCreate(BaseModel):
    """Schema for creating an export."""
    format: Literal["csv", "xlsx"] = Field(default="csv", description="Export format")


class ExportResponse(BaseModel):
    """Schema for export response."""
    id: int
    project_id: int
    format: str
    filename: str
    file_path: str
    status: str
    records_exported: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExportListResponse(BaseModel):
    """Schema for listing exports."""
    id: int
    project_id: int
    format: str
    filename: str
    status: str
    records_exported: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
