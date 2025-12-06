"""Mapping profile management endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.mapping import MappingProfile, MappingEdge, MappingType, TransformType
from app.models.schema import SchemaDefinition, FieldDefinition
from app.models.project import Project
from app.models.file import SourceFile
from app.services.file_parser import FileParser, FileParserError
from app.services.mapping_engine import MappingEngine

router = APIRouter()


# Pydantic schemas
class MappingEdgeCreate(BaseModel):
    source_field_id: Optional[int] = None
    target_field_id: int
    mapping_type: MappingType = MappingType.DIRECT
    transform_type: TransformType = TransformType.NONE
    transform_config: Optional[dict] = None
    constant_value: Optional[str] = None
    lookup_table: Optional[dict] = None
    additional_source_fields: Optional[list[int]] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class MappingEdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    profile_id: int
    source_field_id: Optional[int]
    target_field_id: int
    mapping_type: MappingType
    transform_type: TransformType
    transform_config: Optional[dict]
    constant_value: Optional[str]
    lookup_table: Optional[dict]
    additional_source_fields: Optional[list]
    position_x: Optional[float]
    position_y: Optional[float]


class MappingProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_schema_id: Optional[int] = None
    target_schema_id: Optional[int] = None


class MappingProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    name: str
    description: Optional[str]
    source_schema_id: Optional[int]
    target_schema_id: Optional[int]
    version: int
    is_active: bool
    layout_json: Optional[dict]
    created_at: datetime
    updated_at: datetime


class MappingProfileWithEdgesResponse(MappingProfileResponse):
    edges: list[MappingEdgeResponse]


class LayoutUpdate(BaseModel):
    layout_json: dict


class PreviewMappingRequest(BaseModel):
    source_field_name: str
    mapping_type: MappingType = MappingType.DIRECT
    transform_type: TransformType = TransformType.NONE
    transform_config: Optional[dict] = None
    constant_value: Optional[str] = None
    lookup_table: Optional[dict] = None
    additional_source_fields: Optional[list[str]] = None


@router.post("/project/{project_id}", response_model=MappingProfileResponse)
async def create_mapping_profile(
    project_id: int,
    profile_data: MappingProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new mapping profile."""
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
    
    profile = MappingProfile(
        project_id=project_id,
        name=profile_data.name,
        description=profile_data.description,
        source_schema_id=profile_data.source_schema_id,
        target_schema_id=profile_data.target_schema_id
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return MappingProfileResponse.model_validate(profile)


@router.get("/project/{project_id}", response_model=list[MappingProfileResponse])
async def list_project_profiles(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all mapping profiles for a project."""
    result = await db.execute(
        select(MappingProfile)
        .where(MappingProfile.project_id == project_id)
        .order_by(MappingProfile.created_at.desc())
    )
    profiles = result.scalars().all()
    
    return [MappingProfileResponse.model_validate(p) for p in profiles]


@router.get("/{profile_id}", response_model=MappingProfileWithEdgesResponse)
async def get_mapping_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get mapping profile with all edges."""
    result = await db.execute(
        select(MappingProfile)
        .where(MappingProfile.id == profile_id)
        .options(selectinload(MappingProfile.edges))
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping profile {profile_id} not found"
        )
    
    return MappingProfileWithEdgesResponse(
        id=profile.id,
        project_id=profile.project_id,
        name=profile.name,
        description=profile.description,
        source_schema_id=profile.source_schema_id,
        target_schema_id=profile.target_schema_id,
        version=profile.version,
        is_active=profile.is_active,
        layout_json=profile.layout_json,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        edges=[MappingEdgeResponse.model_validate(e) for e in profile.edges]
    )


@router.post("/{profile_id}/edges", response_model=MappingEdgeResponse)
async def add_mapping_edge(
    profile_id: int,
    edge_data: MappingEdgeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a mapping edge to a profile."""
    result = await db.execute(
        select(MappingProfile).where(MappingProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping profile {profile_id} not found"
        )
    
    edge = MappingEdge(
        profile_id=profile_id,
        source_field_id=edge_data.source_field_id,
        target_field_id=edge_data.target_field_id,
        mapping_type=edge_data.mapping_type,
        transform_type=edge_data.transform_type,
        transform_config=edge_data.transform_config,
        constant_value=edge_data.constant_value,
        lookup_table=edge_data.lookup_table,
        additional_source_fields=edge_data.additional_source_fields,
        position_x=edge_data.position_x,
        position_y=edge_data.position_y
    )
    db.add(edge)
    
    # Increment profile version
    profile.version += 1
    profile.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(edge)
    
    return MappingEdgeResponse.model_validate(edge)


@router.put("/{profile_id}/edges/{edge_id}", response_model=MappingEdgeResponse)
async def update_mapping_edge(
    profile_id: int,
    edge_id: int,
    edge_data: MappingEdgeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update a mapping edge."""
    result = await db.execute(
        select(MappingEdge)
        .where(MappingEdge.id == edge_id, MappingEdge.profile_id == profile_id)
    )
    edge = result.scalar_one_or_none()
    
    if not edge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping edge {edge_id} not found"
        )
    
    # Update edge
    edge.source_field_id = edge_data.source_field_id
    edge.target_field_id = edge_data.target_field_id
    edge.mapping_type = edge_data.mapping_type
    edge.transform_type = edge_data.transform_type
    edge.transform_config = edge_data.transform_config
    edge.constant_value = edge_data.constant_value
    edge.lookup_table = edge_data.lookup_table
    edge.additional_source_fields = edge_data.additional_source_fields
    edge.position_x = edge_data.position_x
    edge.position_y = edge_data.position_y
    
    await db.commit()
    await db.refresh(edge)
    
    return MappingEdgeResponse.model_validate(edge)


@router.delete("/{profile_id}/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mapping_edge(
    profile_id: int,
    edge_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a mapping edge."""
    result = await db.execute(
        select(MappingEdge)
        .where(MappingEdge.id == edge_id, MappingEdge.profile_id == profile_id)
    )
    edge = result.scalar_one_or_none()
    
    if not edge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping edge {edge_id} not found"
        )
    
    await db.delete(edge)
    await db.commit()


@router.put("/{profile_id}/layout", response_model=MappingProfileResponse)
async def update_profile_layout(
    profile_id: int,
    layout: LayoutUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update the ReactFlow layout for a profile."""
    result = await db.execute(
        select(MappingProfile).where(MappingProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping profile {profile_id} not found"
        )
    
    profile.layout_json = layout.layout_json
    profile.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(profile)
    
    return MappingProfileResponse.model_validate(profile)


@router.post("/{profile_id}/preview")
async def preview_mapping(
    profile_id: int,
    file_id: int,
    rows: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Preview mapping results on sample data."""
    # Get profile with edges
    result = await db.execute(
        select(MappingProfile)
        .where(MappingProfile.id == profile_id)
        .options(selectinload(MappingProfile.edges))
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping profile {profile_id} not found"
        )
    
    # Get source file
    file_result = await db.execute(
        select(SourceFile).where(SourceFile.id == file_id)
    )
    source_file = file_result.scalar_one_or_none()
    
    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
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
    
    # Build edge configurations with field names
    edge_configs = []
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
        
        # Get target field name
        target_result = await db.execute(
            select(FieldDefinition).where(FieldDefinition.id == edge.target_field_id)
        )
        target_field = target_result.scalar_one_or_none()
        target_field_name = target_field.name if target_field else f"field_{edge.target_field_id}"
        
        edge_configs.append({
            'source_field_name': source_field_name,
            'target_field_name': target_field_name,
            'mapping_type': edge.mapping_type.value,
            'transform_type': edge.transform_type.value,
            'transform_config': edge.transform_config,
            'constant_value': edge.constant_value,
            'lookup_table': edge.lookup_table,
            'additional_source_fields': edge.additional_source_fields
        })
    
    # Get target field names
    target_field_names = [e['target_field_name'] for e in edge_configs]
    
    # Apply mappings
    transformed_df, warnings = MappingEngine.apply_mappings(
        df.head(rows),
        edge_configs,
        target_field_names
    )
    
    return {
        "profile_id": profile_id,
        "source_rows": rows,
        "source_data": df.head(rows).to_dict(orient='records'),
        "transformed_data": transformed_df.to_dict(orient='records'),
        "warnings": warnings[:50],  # Limit warnings
        "warnings_count": len(warnings)
    }


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mapping_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a mapping profile."""
    result = await db.execute(
        select(MappingProfile).where(MappingProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping profile {profile_id} not found"
        )
    
    await db.delete(profile)
    await db.commit()
