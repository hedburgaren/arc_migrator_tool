"""File management endpoints."""

import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.file import SourceFile
from app.models.project import Project
from app.services.file_parser import FileParser, FileParserError

router = APIRouter()


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    encoding: Optional[str]
    row_count: Optional[int]
    column_count: Optional[int]
    sheet_name: Optional[str]
    uploaded_at: datetime


class FilePreviewResponse(BaseModel):
    file: FileResponse
    columns: list[str]
    preview_data: list[dict]
    total_rows: int


class ExcelSheetsResponse(BaseModel):
    file_id: int
    sheets: list[str]


@router.post("/upload/{project_id}", response_model=FileResponse)
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    sheet_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload a data file for a project."""
    # Validate project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    # Validate file
    try:
        FileParser.validate_file(file.filename, file.size)
    except FileParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Ensure upload directory exists
    upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {e}"
        )
    
    # Parse file to get metadata
    try:
        file_type = FileParser.get_file_type(file.filename)
        df, metadata = FileParser.parse_file(file_path, file_type, sheet_name=sheet_name)
    except FileParserError as e:
        # Clean up file on error
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create database record
    source_file = SourceFile(
        project_id=project_id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_type=file_type,
        file_size=file.size,
        encoding=metadata.get('encoding'),
        row_count=metadata.get('row_count'),
        column_count=metadata.get('column_count'),
        sheet_name=metadata.get('sheet_name'),
        metadata_json={'columns': metadata.get('columns', [])}
    )
    
    db.add(source_file)
    await db.commit()
    await db.refresh(source_file)
    
    return FileResponse.model_validate(source_file)


@router.get("/project/{project_id}", response_model=list[FileResponse])
async def list_project_files(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all files for a project."""
    result = await db.execute(
        select(SourceFile)
        .where(SourceFile.project_id == project_id)
        .order_by(SourceFile.uploaded_at.desc())
    )
    files = result.scalars().all()
    
    return [FileResponse.model_validate(f) for f in files]


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get file details."""
    result = await db.execute(
        select(SourceFile).where(SourceFile.id == file_id)
    )
    source_file = result.scalar_one_or_none()
    
    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    
    return FileResponse.model_validate(source_file)


@router.get("/{file_id}/preview", response_model=FilePreviewResponse)
async def get_file_preview(
    file_id: int,
    rows: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get file preview with sample data."""
    result = await db.execute(
        select(SourceFile).where(SourceFile.id == file_id)
    )
    source_file = result.scalar_one_or_none()
    
    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    
    # Limit preview rows
    rows = min(rows, settings.MAX_PREVIEW_ROWS)
    
    try:
        df, _ = FileParser.parse_file(
            source_file.file_path, 
            source_file.file_type,
            sheet_name=source_file.sheet_name
        )
        preview_data = FileParser.get_preview(df, rows)
        columns = list(df.columns)
    except FileParserError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {e}"
        )
    
    return FilePreviewResponse(
        file=FileResponse.model_validate(source_file),
        columns=columns,
        preview_data=preview_data,
        total_rows=source_file.row_count or len(df)
    )


@router.get("/{file_id}/sheets", response_model=ExcelSheetsResponse)
async def get_excel_sheets(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get list of sheets from an Excel file."""
    result = await db.execute(
        select(SourceFile).where(SourceFile.id == file_id)
    )
    source_file = result.scalar_one_or_none()
    
    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    
    if source_file.file_type not in {'xlsx', 'xls'}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not an Excel file"
        )
    
    try:
        sheets = FileParser.get_excel_sheets(source_file.file_path)
    except FileParserError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    return ExcelSheetsResponse(file_id=file_id, sheets=sheets)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a file."""
    result = await db.execute(
        select(SourceFile).where(SourceFile.id == file_id)
    )
    source_file = result.scalar_one_or_none()
    
    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    
    # Delete physical file
    file_path = Path(source_file.file_path)
    file_path.unlink(missing_ok=True)
    
    # Delete database record
    await db.delete(source_file)
    await db.commit()
