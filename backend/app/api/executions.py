"""Execution management endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.execution import ExecutionRun, ExecutionLog, ExecutionMode, ExecutionStatus, LogLevel
from app.models.mapping import MappingProfile
from app.models.schema import FieldDefinition
from app.models.file import SourceFile
from app.models.project import Project, ProjectStatus
from app.services.file_parser import FileParser, FileParserError
from app.services.execution_engine import ExecutionEngine

router = APIRouter()


# Pydantic schemas
class ExecutionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    execution_id: int
    level: LogLevel
    message: str
    record_index: Optional[int]
    field_name: Optional[str]
    source_value: Optional[str]
    target_value: Optional[str]
    timestamp: datetime


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    mapping_profile_id: int
    mode: ExecutionMode
    status: ExecutionStatus
    total_records: Optional[int]
    processed_records: int
    successful_records: int
    failed_records: int
    warnings_count: int
    error_message: Optional[str]
    output_files: Optional[list]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class ExecutionWithLogsResponse(ExecutionResponse):
    logs: list[ExecutionLogResponse]


class ExecutionCreate(BaseModel):
    mapping_profile_id: int
    file_id: int
    mode: ExecutionMode


@router.post("/execute", response_model=ExecutionResponse)
async def execute_migration(
    execution_data: ExecutionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Execute a migration with the specified mode."""
    # Get mapping profile
    profile_result = await db.execute(
        select(MappingProfile)
        .where(MappingProfile.id == execution_data.mapping_profile_id)
        .options(selectinload(MappingProfile.edges))
    )
    profile = profile_result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping profile {execution_data.mapping_profile_id} not found"
        )
    
    # Get source file
    file_result = await db.execute(
        select(SourceFile).where(SourceFile.id == execution_data.file_id)
    )
    source_file = file_result.scalar_one_or_none()
    
    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {execution_data.file_id} not found"
        )
    
    # Parse source file
    try:
        source_df, _ = FileParser.parse_file(
            source_file.file_path,
            source_file.file_type,
            sheet_name=source_file.sheet_name
        )
    except FileParserError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse source file: {e}"
        )
    
    # Build edge configurations
    edge_configs = []
    target_fields = []
    
    for edge in profile.edges:
        # Get source field name
        source_field_name = None
        if edge.source_field_id:
            field_result = await db.execute(
                select(FieldDefinition).where(FieldDefinition.id == edge.source_field_id)
            )
            source_field = field_result.scalar_one_or_none()
            if source_field:
                source_field_name = source_field.name
        
        # Get target field
        target_result = await db.execute(
            select(FieldDefinition).where(FieldDefinition.id == edge.target_field_id)
        )
        target_field = target_result.scalar_one_or_none()
        
        if target_field:
            target_fields.append({
                'name': target_field.name,
                'field_type': target_field.field_type.value,
                'is_required': target_field.is_required
            })
            
            edge_configs.append({
                'source_field_name': source_field_name,
                'target_field_name': target_field.name,
                'mapping_type': edge.mapping_type.value,
                'transform_type': edge.transform_type.value,
                'transform_config': edge.transform_config,
                'constant_value': edge.constant_value,
                'lookup_table': edge.lookup_table,
                'additional_source_fields': edge.additional_source_fields
            })
    
    # Create execution record
    execution = ExecutionRun(
        project_id=profile.project_id,
        mapping_profile_id=profile.id,
        mode=execution_data.mode,
        status=ExecutionStatus.RUNNING,
        started_at=datetime.utcnow()
    )
    db.add(execution)
    await db.flush()
    
    # Execute migration
    result = await ExecutionEngine.execute(
        source_df=source_df,
        edges=edge_configs,
        target_fields=target_fields,
        mode=execution_data.mode,
        project_id=profile.project_id,
        profile_id=profile.id
    )
    
    # Update execution record
    execution.status = result.status
    execution.total_records = result.total_records
    execution.processed_records = result.processed_records
    execution.successful_records = result.successful_records
    execution.failed_records = result.failed_records
    execution.warnings_count = result.warnings_count
    execution.error_message = result.error_message
    execution.output_files = result.output_files
    execution.completed_at = datetime.utcnow()
    
    # Save logs
    for log_data in result.logs:
        log = ExecutionLog(
            execution_id=execution.id,
            level=LogLevel(log_data.get('level', 'info')),
            message=log_data.get('message', ''),
            record_index=log_data.get('record_index'),
            field_name=log_data.get('field_name'),
            source_value=log_data.get('source_value'),
            target_value=log_data.get('target_value')
        )
        db.add(log)
    
    # Update project status
    project_result = await db.execute(
        select(Project).where(Project.id == profile.project_id)
    )
    project = project_result.scalar_one()
    
    if execution_data.mode == ExecutionMode.COMMIT:
        if result.status == ExecutionStatus.COMPLETED:
            project.status = ProjectStatus.COMPLETED
        else:
            project.status = ProjectStatus.FAILED
    
    await db.commit()
    await db.refresh(execution)
    
    return ExecutionResponse.model_validate(execution)


@router.get("/project/{project_id}", response_model=list[ExecutionResponse])
async def list_project_executions(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all executions for a project."""
    result = await db.execute(
        select(ExecutionRun)
        .where(ExecutionRun.project_id == project_id)
        .order_by(ExecutionRun.created_at.desc())
    )
    executions = result.scalars().all()
    
    return [ExecutionResponse.model_validate(e) for e in executions]


@router.get("/{execution_id}", response_model=ExecutionWithLogsResponse)
async def get_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get execution details with logs."""
    result = await db.execute(
        select(ExecutionRun)
        .where(ExecutionRun.id == execution_id)
        .options(selectinload(ExecutionRun.logs))
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )
    
    return ExecutionWithLogsResponse(
        id=execution.id,
        project_id=execution.project_id,
        mapping_profile_id=execution.mapping_profile_id,
        mode=execution.mode,
        status=execution.status,
        total_records=execution.total_records,
        processed_records=execution.processed_records,
        successful_records=execution.successful_records,
        failed_records=execution.failed_records,
        warnings_count=execution.warnings_count,
        error_message=execution.error_message,
        output_files=execution.output_files,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        created_at=execution.created_at,
        logs=[ExecutionLogResponse.model_validate(log) for log in execution.logs]
    )


@router.get("/{execution_id}/preview-data")
async def get_execution_preview_data(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get preview data from a preview execution."""
    result = await db.execute(
        select(ExecutionRun).where(ExecutionRun.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )
    
    if execution.mode != ExecutionMode.PREVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preview data only available for preview executions"
        )
    
    # Return execution metadata (preview data would be cached in a real implementation)
    return {
        "execution_id": execution_id,
        "mode": execution.mode.value,
        "total_records": execution.total_records,
        "processed_records": execution.processed_records,
        "message": "Preview data is available during execution. Use the /execute endpoint with mode=preview for fresh preview."
    }


@router.get("/{execution_id}/output-files")
async def get_execution_output_files(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get output file paths from an execution."""
    result = await db.execute(
        select(ExecutionRun).where(ExecutionRun.id == execution_id)
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution {execution_id} not found"
        )
    
    return {
        "execution_id": execution_id,
        "status": execution.status.value,
        "output_files": execution.output_files or []
    }
