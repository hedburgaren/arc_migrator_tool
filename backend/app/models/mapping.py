"""Mapping profile and edge models."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class MappingType(str, enum.Enum):
    """Mapping type enumeration."""
    DIRECT = "direct"  # 1:1 mapping
    TRANSFORM = "transform"  # 1:1 with transformation
    CONCAT = "concat"  # N:1 concatenation
    SPLIT = "split"  # 1:N splitting
    LOOKUP = "lookup"  # Value lookup/mapping
    CONSTANT = "constant"  # Constant value


class TransformType(str, enum.Enum):
    """Transform operation types."""
    NONE = "none"
    LOWERCASE = "lowercase"
    UPPERCASE = "uppercase"
    TRIM = "trim"
    CONCAT = "concat"
    SPLIT = "split"
    REPLACE = "replace"
    FORMAT_DATE = "format_date"
    TO_NUMBER = "to_number"
    TO_STRING = "to_string"
    LOOKUP = "lookup"
    CUSTOM = "custom"


class MappingProfile(Base):
    """Mapping profile for a project."""
    
    __tablename__ = "mapping_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_schema_id: Mapped[int | None] = mapped_column(ForeignKey("schema_definitions.id"), nullable=True)
    target_schema_id: Mapped[int | None] = mapped_column(ForeignKey("schema_definitions.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(default=True)
    layout_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Store ReactFlow layout
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    project = relationship("Project", back_populates="mapping_profiles")
    edges = relationship("MappingEdge", back_populates="profile", cascade="all, delete-orphan")


class MappingEdge(Base):
    """Mapping edge connecting source to target fields."""
    
    __tablename__ = "mapping_edges"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("mapping_profiles.id"), nullable=False)
    source_field_id: Mapped[int | None] = mapped_column(ForeignKey("field_definitions.id"), nullable=True)
    target_field_id: Mapped[int] = mapped_column(ForeignKey("field_definitions.id"), nullable=False)
    mapping_type: Mapped[MappingType] = mapped_column(Enum(MappingType), default=MappingType.DIRECT)
    transform_type: Mapped[TransformType] = mapped_column(Enum(TransformType), default=TransformType.NONE)
    transform_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Parameters for transform
    constant_value: Mapped[str | None] = mapped_column(Text, nullable=True)  # For constant mappings
    lookup_table: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # For lookup mappings
    additional_source_fields: Mapped[list | None] = mapped_column(JSON, nullable=True)  # For N:1 mappings
    position_x: Mapped[float | None] = mapped_column(Float, nullable=True)
    position_y: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Relationships
    profile = relationship("MappingProfile", back_populates="edges")
