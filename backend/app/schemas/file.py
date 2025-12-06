"""
Pydantic schemas for file operations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FileResponse(BaseModel):
    """Schema for file metadata response."""
    
    id: int
    filename: str
    file_path: str
    file_size: int
    file_type: str
    upload_timestamp: datetime
    status: str
    schema_analyzed: bool = False
    column_count: Optional[int] = None
    row_count: Optional[int] = None
    encoding: Optional[str] = None
    
    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    
    id: int
    filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime
    message: str
