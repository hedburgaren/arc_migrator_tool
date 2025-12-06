"""
Validation endpoints for files and mappings.
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.file import File
from app.models.validation_report import ValidationReport
from app.schemas.validation import (
    FileValidationRequest,
    MappingValidationRequest,
    ValidationReportResponse
)
from app.services.file_validator import FileValidator
from app.services.mapping_validator import MappingValidator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/files/{file_id}/validate", response_model=ValidationReportResponse)
async def validate_file(
    file_id: int,
    request: FileValidationRequest = FileValidationRequest(),
    db: Session = Depends(get_db)
):
    """
    Validate an uploaded file.
    
    Args:
        file_id: File ID
        request: Validation configuration
        db: Database session
        
    Returns:
        ValidationReportResponse: Validation results
    """
    # Get file
    db_file = db.query(File).filter(File.id == file_id).first()
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found"
        )
    
    try:
        # Run validation
        validator = FileValidator()
        validation_status, issues = validator.validate_file(
            db_file.file_path,
            check_encoding=request.check_encoding,
            check_structure=request.check_structure,
            check_data_quality=request.check_data_quality,
            max_file_size_mb=request.max_file_size_mb
        )
        
        # Create validation report
        db_report = ValidationReport(
            file_id=file_id,
            validation_type="file",
            status=validation_status,
            issues=issues
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        logger.info(f"File validation completed for file {file_id}: {validation_status}")
        
        return db_report
        
    except Exception as e:
        logger.error(f"File validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/projects/{project_id}/mappings/validate", response_model=ValidationReportResponse)
async def validate_mappings(
    project_id: int,
    request: MappingValidationRequest = MappingValidationRequest(),
    db: Session = Depends(get_db)
):
    """
    Validate field mappings for a project.
    
    Args:
        project_id: Project ID
        request: Validation configuration
        db: Database session
        
    Returns:
        ValidationReportResponse: Validation results
    """
    # Get project
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get mappings
    mappings = db_project.mappings
    if not mappings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No mappings defined for this project"
        )
    
    try:
        # Convert mappings to dict format
        mapping_dicts = [
            {
                "id": m.id,
                "source_field": m.source_field,
                "target_field": m.target_field,
                "transform_type": m.transform_type,
                "transform_config": m.transform_config or {}
            }
            for m in mappings
        ]
        
        # Get source schema (from most recent analyzed file)
        db_file = db.query(File).filter(File.schema_analyzed == True).order_by(File.upload_timestamp.desc()).first()
        
        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No analyzed files found. Cannot validate mappings without source schema."
            )
        
        # Get source field names
        source_schema = [s.column_name for s in db_file.schemas]
        
        # Run validation
        validator = MappingValidator()
        validation_status, issues = validator.validate_mappings(
            mapping_dicts,
            source_schema,
            check_completeness=request.check_completeness,
            check_type_compatibility=request.check_type_compatibility,
            check_circular_deps=request.check_circular_deps,
            required_fields=request.required_fields or []
        )
        
        # Update mappings with validation errors
        for mapping in mappings:
            mapping_issues = [
                issue for issue in issues
                if issue.get('details', {}).get('mapping_id') == mapping.id
            ]
            if mapping_issues:
                mapping.validation_errors = mapping_issues
        
        # Update project validation status
        db_project.validation_status = validation_status
        
        # Create validation report
        db_report = ValidationReport(
            project_id=project_id,
            validation_type="mapping",
            status=validation_status,
            issues=issues
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        logger.info(f"Mapping validation completed for project {project_id}: {validation_status}")
        
        return db_report
        
    except Exception as e:
        logger.error(f"Mapping validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/projects/{project_id}/validation-report", response_model=List[ValidationReportResponse])
async def get_validation_reports(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get validation reports for a project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        List of validation reports
    """
    # Check if project exists
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get validation reports
    reports = db.query(ValidationReport).filter(
        ValidationReport.project_id == project_id
    ).order_by(ValidationReport.created_at.desc()).all()
    
    return reports
