"""
Schema analysis endpoints.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.file import File
from app.models.schema import Schema
from app.schemas.schema import FileSchemaResponse, SchemaAnalysisRequest, ColumnSchema
from app.services.schema_analyzer import SchemaAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{file_id}/analyze", status_code=status.HTTP_200_OK)
async def analyze_file_schema(
    file_id: int,
    request: SchemaAnalysisRequest = SchemaAnalysisRequest(),
    db: Session = Depends(get_db)
):
    """
    Trigger schema analysis for a file.
    
    Args:
        file_id: File ID to analyze
        request: Analysis configuration
        db: Database session
        
    Returns:
        Success message
    """
    # Get file from database
    db_file = db.query(File).filter(File.id == file_id).first()
    
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found"
        )
    
    # Check if file exists on disk
    import os
    if not os.path.exists(db_file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found on disk: {db_file.file_path}"
        )
    
    try:
        # Update file status
        db_file.status = "processing"
        db.commit()
        
        # Analyze file
        analyzer = SchemaAnalyzer(sample_size=request.sample_size)
        analysis_result = analyzer.analyze_file(db_file.file_path)
        
        # Delete existing schema entries for this file
        db.query(Schema).filter(Schema.file_id == file_id).delete()
        
        # Save schema to database
        for col_meta in analysis_result['columns']:
            schema_entry = Schema(
                file_id=file_id,
                column_name=col_meta['column_name'],
                column_index=col_meta['column_index'],
                data_type=col_meta['data_type'],
                sample_values=col_meta['sample_values'],
                null_count=col_meta['null_count'],
                unique_count=col_meta['unique_count'],
                statistics=col_meta['statistics']
            )
            db.add(schema_entry)
        
        # Update file metadata
        db_file.schema_analyzed = True
        db_file.row_count = analysis_result['row_count']
        db_file.column_count = analysis_result['column_count']
        db_file.encoding = analysis_result['encoding']
        db_file.status = "uploaded"
        
        db.commit()
        
        logger.info(f"Successfully analyzed file {file_id}: {db_file.filename}")
        
        return {
            "message": "Schema analysis completed successfully",
            "file_id": file_id,
            "row_count": analysis_result['row_count'],
            "column_count": analysis_result['column_count']
        }
        
    except Exception as e:
        db_file.status = "error"
        db.commit()
        logger.error(f"Failed to analyze file {file_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze file: {str(e)}"
        )


@router.get("/{file_id}/schema", response_model=FileSchemaResponse)
async def get_file_schema(
    file_id: int,
    db: Session = Depends(get_db)
):
    """
    Get schema information for a file.
    
    Args:
        file_id: File ID
        db: Database session
        
    Returns:
        FileSchemaResponse: Schema information
    """
    # Get file from database
    db_file = db.query(File).filter(File.id == file_id).first()
    
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found"
        )
    
    # Check if schema has been analyzed
    if not db_file.schema_analyzed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schema has not been analyzed yet. Please trigger analysis first."
        )
    
    # Get schema entries
    schema_entries = db.query(Schema).filter(
        Schema.file_id == file_id
    ).order_by(Schema.column_index).all()
    
    if not schema_entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schema data not found"
        )
    
    # Convert to response model
    columns = [ColumnSchema.model_validate(entry) for entry in schema_entries]
    
    return FileSchemaResponse(
        file_id=file_id,
        filename=db_file.filename,
        row_count=db_file.row_count or 0,
        column_count=db_file.column_count or 0,
        encoding=db_file.encoding,
        columns=columns
    )
