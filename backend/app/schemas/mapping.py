"""
Pydantic schemas for mapping operations.
"""
from datetime import datetime
from typing import Optional, Any, Dict, Literal
from pydantic import BaseModel, Field


class MappingBase(BaseModel):
    """Base schema for mapping."""
    source_field: Optional[str] = Field(default=None, max_length=255)
    target_field: str = Field(..., min_length=1, max_length=255)
    transform_type: Literal["1:1", "concat", "constant", "lookup", "split", "custom"] = Field(default="1:1")
    transform_config: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None


class MappingCreate(MappingBase):
    """Schema for creating a mapping."""
    pass


class MappingUpdate(BaseModel):
    """Schema for updating a mapping."""
    source_field: Optional[str] = Field(None, min_length=1, max_length=255)
    target_field: Optional[str] = Field(None, min_length=1, max_length=255)
    transform_type: Optional[Literal["1:1", "concat", "constant", "lookup", "split", "custom"]] = None
    transform_config: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None


class MappingResponse(MappingBase):
    """Schema for mapping response."""
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
