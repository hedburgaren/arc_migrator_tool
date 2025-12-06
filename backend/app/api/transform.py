"""
Transform and preview endpoints.
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.file import File
from app.schemas.validation import TransformPreviewRequest, TransformPreviewResponse, TransformPreviewRow
from app.services.transform_engine import TransformEngine
from app.services.schema_analyzer import SchemaAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/projects/{project_id}/preview", response_model=TransformPreviewResponse)
async def preview_transformations(
    project_id: int,
    request: TransformPreviewRequest = TransformPreviewRequest(),
    db: Session = Depends(get_db)
):
    """
    Preview transformed data without committing changes.
    
    Shows sample rows of original vs transformed data side-by-side.
    
    Args:
        project_id: Project ID
        request: Preview configuration
        db: Database session
        
    Returns:
        TransformPreviewResponse: Preview data with original and transformed rows
    """
    # Get project
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get mappings for this project
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
    
    # For now, we need to get source data from somewhere
    # In a real implementation, this would come from a file or execution
    # Let's try to find a file associated with the project
    # This is a simplified implementation - in production, you'd have explicit project-file relationships
    
    # Try to get the most recently uploaded file (as a proxy for source data)
    db_file = db.query(File).filter(File.schema_analyzed == True).order_by(File.upload_timestamp.desc()).first()
    
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analyzed files found. Please upload and analyze a source file first."
        )
    
    try:
        # Read source data
        analyzer = SchemaAnalyzer()
        source_df, _ = analyzer.read_file(db_file.file_path)
        
        # Limit to requested sample
        start_row = request.start_row
        end_row = start_row + request.sample_size
        sample_df = source_df.iloc[start_row:end_row]
        
        # Apply transformations
        transform_engine = TransformEngine()
        transformed_df, errors = transform_engine.execute_transformations(sample_df, mapping_dicts)
        
        # Build preview rows
        preview_rows = []
        for idx, (_, orig_row) in enumerate(sample_df.iterrows()):
            row_number = start_row + idx
            
            # Get transformed data for this row
            if not transformed_df.empty and idx < len(transformed_df):
                trans_row = transformed_df.iloc[idx]
                transformed_data = trans_row.to_dict()
            else:
                transformed_data = {}
            
            # Collect row-specific errors
            row_errors = [
                e.get('error', str(e))
                for e in errors
                if 'row' in e and e.get('row') == row_number
            ]
            
            preview_rows.append(TransformPreviewRow(
                row_number=row_number,
                original_data=orig_row.to_dict(),
                transformed_data=transformed_data,
                errors=row_errors if row_errors else None
            ))
        
        return TransformPreviewResponse(
            project_id=project_id,
            total_rows=len(source_df),
            preview_rows=preview_rows,
            mappings_applied=len(mapping_dicts),
            transformation_errors=errors
        )
        
    except Exception as e:
        logger.error(f"Preview transformation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )


@router.get("/projects/{project_id}/transform-status")
async def get_transform_status(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get transformation status for a project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Status information
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get mapping count
    mapping_count = len(db_project.mappings)
    
    # Get latest execution
    latest_execution = None
    if db_project.executions:
        latest_execution = sorted(db_project.executions, key=lambda x: x.start_time or "", reverse=True)[0]
    
    return {
        "project_id": project_id,
        "project_name": db_project.name,
        "status": db_project.status,
        "validation_status": db_project.validation_status,
        "mapping_count": mapping_count,
        "latest_execution": {
            "id": latest_execution.id,
            "type": latest_execution.execution_type,
            "status": latest_execution.status,
            "records_processed": latest_execution.records_processed,
            "start_time": latest_execution.start_time.isoformat() if latest_execution.start_time else None
        } if latest_execution else None
    }
