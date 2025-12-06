"""
Export and download endpoints.
"""
import os
import logging
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.export import Export
from app.models.file import File
from app.schemas.export import ExportCreate, ExportResponse, ExportListResponse
from app.services.transform_engine import TransformEngine
from app.services.export_service import ExportService
from app.services.schema_analyzer import SchemaAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/projects/{project_id}/export", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def create_export(
    project_id: int,
    export_request: ExportCreate,
    db: Session = Depends(get_db)
):
    """
    Generate export file from transformed data.
    
    Args:
        project_id: Project ID
        export_request: Export configuration
        db: Database session
        
    Returns:
        ExportResponse: Export metadata
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
    
    # Get source data (simplified - get most recent analyzed file)
    db_file = db.query(File).filter(File.schema_analyzed == True).order_by(File.upload_timestamp.desc()).first()
    
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analyzed files found. Please upload and analyze a source file first."
        )
    
    # Create export record
    export_filename = f"export_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_request.format}"
    
    db_export = Export(
        project_id=project_id,
        format=export_request.format,
        filename=export_filename,
        file_path="",  # Will be updated after generation
        status="generating"
    )
    db.add(db_export)
    db.commit()
    db.refresh(db_export)
    
    try:
        # Read source data
        analyzer = SchemaAnalyzer()
        source_df, _ = analyzer.read_file(db_file.file_path)
        
        # Apply transformations
        transform_engine = TransformEngine()
        transformed_df, errors = transform_engine.execute_transformations(source_df, mapping_dicts)
        
        if transformed_df.empty:
            raise ValueError("Transformation produced no data")
        
        # Generate export file
        export_service = ExportService()
        file_path = export_service.generate_export(
            transformed_df,
            format=export_request.format,
            filename=f"project_{project_id}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Update export record
        db_export.file_path = file_path
        db_export.status = "ready"
        db_export.records_exported = len(transformed_df)
        db_export.expires_at = datetime.utcnow() + timedelta(hours=24)
        
        db.commit()
        db.refresh(db_export)
        
        logger.info(f"Export {db_export.id} generated successfully: {file_path}")
        
        return db_export
        
    except Exception as e:
        logger.error(f"Export generation failed: {str(e)}")
        db_export.status = "error"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate export: {str(e)}"
        )


@router.get("/projects/{project_id}/export/{export_id}")
async def download_export(
    project_id: int,
    export_id: int,
    db: Session = Depends(get_db)
):
    """
    Download a generated export file.
    
    Args:
        project_id: Project ID
        export_id: Export ID
        db: Database session
        
    Returns:
        File download
    """
    # Get export
    db_export = db.query(Export).filter(
        Export.id == export_id,
        Export.project_id == project_id
    ).first()
    
    if not db_export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Export with id {export_id} not found for project {project_id}"
        )
    
    # Check status
    if db_export.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Export is not ready (status: {db_export.status})"
        )
    
    # Check if expired
    if db_export.expires_at and db_export.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Export has expired"
        )
    
    # Check if file exists
    if not os.path.exists(db_export.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not found on disk"
        )
    
    # Determine media type
    media_type = "text/csv" if db_export.format == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return FileResponse(
        path=db_export.file_path,
        filename=db_export.filename,
        media_type=media_type
    )


@router.get("/projects/{project_id}/exports", response_model=List[ExportListResponse])
async def list_exports(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    List all exports for a project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        List of exports
    """
    # Check if project exists
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get exports
    exports = db.query(Export).filter(
        Export.project_id == project_id
    ).order_by(Export.created_at.desc()).all()
    
    return exports
