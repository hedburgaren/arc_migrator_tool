"""
File upload and management endpoints.
"""
import os
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File as FastAPIFile, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.file import File
from app.schemas.file import FileResponse, FileUploadResponse

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# File validation settings
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}


def validate_file(file: UploadFile) -> None:
    """
    Validate uploaded file.
    
    Args:
        file: Uploaded file
        
    Raises:
        HTTPException: If file validation fails
    """
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type if available and not generic
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES and file.content_type != "application/octet-stream":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Expected CSV or Excel file."
        )


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file (CSV or Excel).
    
    Args:
        file: File to upload
        db: Database session
        
    Returns:
        FileUploadResponse: Upload result with file metadata
    """
    # Validate file
    validate_file(file)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Read and validate file size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024):.0f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create database record
    db_file = File(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file.content_type or "application/octet-stream",
        status="uploaded"
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return FileUploadResponse(
        id=db_file.id,
        filename=db_file.filename,
        file_size=db_file.file_size,
        file_type=db_file.file_type,
        upload_timestamp=db_file.upload_timestamp,
        message="File uploaded successfully"
    )


@router.get("", response_model=List[FileResponse])
async def list_files(db: Session = Depends(get_db)):
    """
    Get list of all uploaded files.
    
    Args:
        db: Database session
        
    Returns:
        List[FileResponse]: List of file metadata
    """
    files = db.query(File).order_by(File.upload_timestamp.desc()).all()
    return files


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: int, db: Session = Depends(get_db)):
    """
    Get metadata for a specific file.
    
    Args:
        file_id: File ID
        db: Database session
        
    Returns:
        FileResponse: File metadata
    """
    db_file = db.query(File).filter(File.id == file_id).first()
    
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found"
        )
    
    return db_file


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """
    Delete a file and its metadata.
    
    Args:
        file_id: File ID
        db: Database session
    """
    db_file = db.query(File).filter(File.id == file_id).first()
    
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found"
        )
    
    # Delete file from disk
    try:
        if os.path.exists(db_file.file_path):
            os.remove(db_file.file_path)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Warning: Failed to delete file from disk: {e}")
    
    # Delete database record
    db.delete(db_file)
    db.commit()
