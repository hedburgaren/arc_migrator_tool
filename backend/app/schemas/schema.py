"""
Pydantic schemas for schema operations.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ColumnSchema(BaseModel):
    """Schema for a single column."""
    
    id: int
    column_name: str
    column_index: int
    data_type: str
    sample_values: Optional[List[Any]] = None
    null_count: int
    unique_count: int
    statistics: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class FileSchemaResponse(BaseModel):
    """Schema response for a file with all columns."""
    
    file_id: int
    filename: str
    row_count: int
    column_count: int
    encoding: Optional[str]
    columns: List[ColumnSchema]


class SchemaAnalysisRequest(BaseModel):
    """Request to trigger schema analysis."""
    
    sample_size: Optional[int] = 5  # Number of sample values to extract
