"""Schema management endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.schema import SchemaDefinition, FieldDefinition, SchemaType, FieldType
from app.models.file import SourceFile
from app.models.project import Project
from app.services.file_parser import FileParser, FileParserError
from app.services.schema_discovery import SchemaDiscoveryService

router = APIRouter()


# Pydantic schemas
class FieldDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    schema_id: int
    name: str
    display_name: Optional[str]
    field_type: FieldType
    is_required: bool
    is_primary_key: bool
    is_lookup: bool
    unique_values_count: Optional[int]
    sample_values: Optional[list]
    position: int


class SchemaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    file_id: Optional[int]
    name: str
    schema_type: SchemaType
    system_type: str
    description: Optional[str]
    created_at: datetime


class SchemaWithFieldsResponse(SchemaResponse):
    fields: list[FieldDefinitionResponse]


class SchemaCreate(BaseModel):
    name: str
    schema_type: SchemaType
    system_type: str
    description: Optional[str] = None


class FieldCreate(BaseModel):
    name: str
    display_name: Optional[str] = None
    field_type: FieldType = FieldType.STRING
    is_required: bool = False
    is_primary_key: bool = False
    is_lookup: bool = False
    position: int = 0


class DiscoverSchemaRequest(BaseModel):
    file_id: int
    name: str
    system_type: str = "csv"


@router.post("/discover", response_model=SchemaWithFieldsResponse)
async def discover_schema_from_file(
    request: DiscoverSchemaRequest,
    db: AsyncSession = Depends(get_db)
):
    """Discover schema from an uploaded file."""
    # Get file
    result = await db.execute(
        select(SourceFile).where(SourceFile.id == request.file_id)
    )
    source_file = result.scalar_one_or_none()
    
    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {request.file_id} not found"
        )
    
    # Parse file
    try:
        df, _ = FileParser.parse_file(
            source_file.file_path,
            source_file.file_type,
            sheet_name=source_file.sheet_name
        )
    except FileParserError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse file: {e}"
        )
    
    # Discover schema
    schema_info = SchemaDiscoveryService.discover_schema(df, request.name)
    
    # Create schema definition
    schema_def = SchemaDefinition(
        project_id=source_file.project_id,
        file_id=source_file.id,
        name=request.name,
        schema_type=SchemaType.SOURCE,
        system_type=request.system_type,
        metadata_json={
            'row_count': schema_info['row_count'],
            'column_count': schema_info['column_count'],
        }
    )
    db.add(schema_def)
    await db.flush()  # Get the ID
    
    # Create field definitions
    for field_info in schema_info['fields']:
        field_def = FieldDefinition(
            schema_id=schema_def.id,
            name=field_info['name'],
            display_name=field_info['display_name'],
            field_type=field_info['field_type'],
            is_required=field_info['is_required'],
            is_primary_key=field_info['is_primary_key'],
            is_lookup=field_info['is_lookup'],
            unique_values_count=field_info['unique_values_count'],
            sample_values=field_info['sample_values'],
            position=field_info['position'],
            metadata_json=field_info.get('metadata_json')
        )
        db.add(field_def)
    
    await db.commit()
    await db.refresh(schema_def)
    
    # Reload with fields
    result = await db.execute(
        select(SchemaDefinition)
        .where(SchemaDefinition.id == schema_def.id)
        .options(selectinload(SchemaDefinition.fields))
    )
    schema_def = result.scalar_one()
    
    return SchemaWithFieldsResponse(
        id=schema_def.id,
        project_id=schema_def.project_id,
        file_id=schema_def.file_id,
        name=schema_def.name,
        schema_type=schema_def.schema_type,
        system_type=schema_def.system_type,
        description=schema_def.description,
        created_at=schema_def.created_at,
        fields=[FieldDefinitionResponse.model_validate(f) for f in schema_def.fields]
    )


@router.post("/project/{project_id}", response_model=SchemaWithFieldsResponse)
async def create_schema(
    project_id: int,
    schema_data: SchemaCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new schema definition."""
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
    
    schema_def = SchemaDefinition(
        project_id=project_id,
        name=schema_data.name,
        schema_type=schema_data.schema_type,
        system_type=schema_data.system_type,
        description=schema_data.description
    )
    db.add(schema_def)
    await db.commit()
    await db.refresh(schema_def)
    
    return SchemaWithFieldsResponse(
        id=schema_def.id,
        project_id=schema_def.project_id,
        file_id=schema_def.file_id,
        name=schema_def.name,
        schema_type=schema_def.schema_type,
        system_type=schema_def.system_type,
        description=schema_def.description,
        created_at=schema_def.created_at,
        fields=[]
    )


@router.get("/project/{project_id}", response_model=list[SchemaResponse])
async def list_project_schemas(
    project_id: int,
    schema_type: Optional[SchemaType] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all schemas for a project."""
    query = select(SchemaDefinition).where(SchemaDefinition.project_id == project_id)
    
    if schema_type:
        query = query.where(SchemaDefinition.schema_type == schema_type)
    
    result = await db.execute(query.order_by(SchemaDefinition.created_at.desc()))
    schemas = result.scalars().all()
    
    return [SchemaResponse.model_validate(s) for s in schemas]


@router.get("/{schema_id}", response_model=SchemaWithFieldsResponse)
async def get_schema(
    schema_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get schema with all fields."""
    result = await db.execute(
        select(SchemaDefinition)
        .where(SchemaDefinition.id == schema_id)
        .options(selectinload(SchemaDefinition.fields))
    )
    schema_def = result.scalar_one_or_none()
    
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema {schema_id} not found"
        )
    
    return SchemaWithFieldsResponse(
        id=schema_def.id,
        project_id=schema_def.project_id,
        file_id=schema_def.file_id,
        name=schema_def.name,
        schema_type=schema_def.schema_type,
        system_type=schema_def.system_type,
        description=schema_def.description,
        created_at=schema_def.created_at,
        fields=[FieldDefinitionResponse.model_validate(f) for f in schema_def.fields]
    )


@router.post("/{schema_id}/fields", response_model=FieldDefinitionResponse)
async def add_field(
    schema_id: int,
    field_data: FieldCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a field to a schema."""
    result = await db.execute(
        select(SchemaDefinition).where(SchemaDefinition.id == schema_id)
    )
    schema_def = result.scalar_one_or_none()
    
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema {schema_id} not found"
        )
    
    field_def = FieldDefinition(
        schema_id=schema_id,
        name=field_data.name,
        display_name=field_data.display_name,
        field_type=field_data.field_type,
        is_required=field_data.is_required,
        is_primary_key=field_data.is_primary_key,
        is_lookup=field_data.is_lookup,
        position=field_data.position
    )
    db.add(field_def)
    await db.commit()
    await db.refresh(field_def)
    
    return FieldDefinitionResponse.model_validate(field_def)


@router.delete("/{schema_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schema(
    schema_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a schema."""
    result = await db.execute(
        select(SchemaDefinition).where(SchemaDefinition.id == schema_id)
    )
    schema_def = result.scalar_one_or_none()
    
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema {schema_id} not found"
        )
    
    await db.delete(schema_def)
    await db.commit()


@router.get("/{schema_id}/lookup-candidates")
async def get_lookup_candidates(
    schema_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get fields that are candidates for lookup tables."""
    result = await db.execute(
        select(SchemaDefinition)
        .where(SchemaDefinition.id == schema_id)
        .options(selectinload(SchemaDefinition.fields))
    )
    schema_def = result.scalar_one_or_none()
    
    if not schema_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema {schema_id} not found"
        )
    
    lookup_fields = [
        FieldDefinitionResponse.model_validate(f)
        for f in schema_def.fields
        if f.is_lookup
    ]
    
    return {
        "schema_id": schema_id,
        "schema_name": schema_def.name,
        "lookup_candidates": lookup_fields
    }
