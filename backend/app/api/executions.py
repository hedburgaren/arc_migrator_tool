"""
Execution management endpoints.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.models.execution import Execution
from app.schemas.execution import ExecutionCreate, ExecutionResponse

router = APIRouter()


@router.post("/projects/{project_id}/executions", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    project_id: int,
    execution: ExecutionCreate,
    db: Session = Depends(get_db)
):
    """
    Start a new execution for a project.
    
    Args:
        project_id: Project ID
        execution: Execution data
        db: Database session
        
    Returns:
        ExecutionResponse: Created execution
    """
    # Check if project exists
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    db_execution = Execution(
        project_id=project_id,
        start_time=datetime.utcnow(),
        **execution.model_dump()
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution


@router.get("/projects/{project_id}/executions", response_model=List[ExecutionResponse])
async def list_project_executions(project_id: int, db: Session = Depends(get_db)):
    """
    Get execution history for a project.
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        List[ExecutionResponse]: List of executions
    """
    # Check if project exists
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    executions = db.query(Execution).filter(Execution.project_id == project_id).order_by(Execution.start_time.desc()).all()
    return executions


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: int, db: Session = Depends(get_db)):
    """
    Get details for a specific execution.
    
    Args:
        execution_id: Execution ID
        db: Database session
        
    Returns:
        ExecutionResponse: Execution details
    """
    db_execution = db.query(Execution).filter(Execution.id == execution_id).first()
    
    if not db_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with id {execution_id} not found"
        )
    
    return db_execution
