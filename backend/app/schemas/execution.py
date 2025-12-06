"""
Pydantic schemas for execution operations.
"""
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ExecutionBase(BaseModel):
    """Base schema for execution."""
    execution_type: str = Field(..., max_length=50)
    status: str = Field(default="pending", max_length=50)


class ExecutionCreate(ExecutionBase):
    """Schema for creating an execution."""
    pass


class ExecutionUpdate(BaseModel):
    """Schema for updating an execution."""
    status: Optional[str] = Field(None, max_length=50)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    records_processed: Optional[int] = None
    records_successful: Optional[int] = None
    records_failed: Optional[int] = None
    execution_log: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None


class ExecutionResponse(ExecutionBase):
    """Schema for execution response."""
    id: int
    project_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    execution_log: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
