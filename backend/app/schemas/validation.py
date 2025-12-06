"""
Pydantic schemas for validation operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    """Schema for a single validation issue."""
    severity: Literal["error", "warning", "info"] = Field(..., description="Issue severity")
    message: str = Field(..., description="Issue description")
    field: Optional[str] = Field(None, description="Related field name")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class ValidationReportCreate(BaseModel):
    """Schema for creating a validation report."""
    project_id: Optional[int] = None
    file_id: Optional[int] = None
    validation_type: Literal["file", "mapping", "data"] = Field(..., description="Type of validation")
    status: Literal["passed", "warning", "failed"] = Field(..., description="Validation status")
    issues: Optional[List[ValidationIssue]] = Field(default_factory=list, description="List of issues found")


class ValidationReportResponse(BaseModel):
    """Schema for validation report response."""
    id: int
    project_id: Optional[int] = None
    file_id: Optional[int] = None
    validation_type: str
    status: str
    issues: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileValidationRequest(BaseModel):
    """Schema for file validation request."""
    check_encoding: bool = Field(default=True, description="Check file encoding")
    check_structure: bool = Field(default=True, description="Check file structure")
    check_data_quality: bool = Field(default=True, description="Check data quality")
    max_file_size_mb: int = Field(default=100, description="Maximum file size in MB")


class MappingValidationRequest(BaseModel):
    """Schema for mapping validation request."""
    check_completeness: bool = Field(default=True, description="Check mapping completeness")
    check_type_compatibility: bool = Field(default=True, description="Check data type compatibility")
    check_circular_deps: bool = Field(default=True, description="Check for circular dependencies")
    required_fields: Optional[List[str]] = Field(default_factory=list, description="List of required target fields")


class TransformPreviewRequest(BaseModel):
    """Schema for transform preview request."""
    sample_size: int = Field(default=10, ge=1, le=100, description="Number of rows to preview")
    start_row: int = Field(default=0, ge=0, description="Starting row for preview")


class TransformPreviewRow(BaseModel):
    """Schema for a single preview row."""
    row_number: int
    original_data: Dict[str, Any]
    transformed_data: Dict[str, Any]
    errors: Optional[List[str]] = None


class TransformPreviewResponse(BaseModel):
    """Schema for transform preview response."""
    project_id: int
    total_rows: int
    preview_rows: List[TransformPreviewRow]
    mappings_applied: int
    transformation_errors: List[Dict[str, Any]] = Field(default_factory=list)
