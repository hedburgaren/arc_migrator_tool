"""
Mapping management endpoints.
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.mapping import Mapping
from app.schemas.mapping import MappingCreate, MappingUpdate, MappingResponse

router = APIRouter()


@router.post("/projects/{project_id}/mappings", response_model=MappingResponse, status_code=status.HTTP_201_CREATED)
async def create_mapping(
    project_id: int,
    mapping: MappingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new mapping for a project.
    
    Args:
        project_id: Project ID
        mapping: Mapping data
        db: Database session
        
    Returns:
        MappingResponse: Created mapping
    """
    # Check if project exists
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    db_mapping = Mapping(project_id=project_id, **mapping.model_dump())
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


@router.get("/projects/{project_id}/mappings", response_model=List[MappingResponse])
async def list_project_mappings(project_id: int, db: Session = Depends(get_db)):
    """
    Get all mappings for a project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        List[MappingResponse]: List of mappings
    """
    # Check if project exists
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    mappings = db.query(Mapping).filter(Mapping.project_id == project_id).order_by(Mapping.created_at).all()
    return mappings


@router.put("/mappings/{mapping_id}", response_model=MappingResponse)
async def update_mapping(
    mapping_id: int,
    mapping: MappingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a mapping.
    
    Args:
        mapping_id: Mapping ID
        mapping: Updated mapping data
        db: Database session
        
    Returns:
        MappingResponse: Updated mapping
    """
    db_mapping = db.query(Mapping).filter(Mapping.id == mapping_id).first()
    
    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping with id {mapping_id} not found"
        )
    
    # Update only provided fields
    update_data = mapping.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mapping, field, value)
    
    db.commit()
    db.refresh(db_mapping)
    return db_mapping


@router.delete("/mappings/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """
    Delete a mapping.
    
    Args:
        mapping_id: Mapping ID
        db: Database session
    """
    db_mapping = db.query(Mapping).filter(Mapping.id == mapping_id).first()
    
    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping with id {mapping_id} not found"
        )
    
    db.delete(db_mapping)
    db.commit()
