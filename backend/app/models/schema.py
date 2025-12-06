"""Schema definition models."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class SchemaType(str, enum.Enum):
    """Schema type enumeration."""
    SOURCE = "source"
    TARGET = "target"


class FieldType(str, enum.Enum):
    """Field data type enumeration."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENUM = "enum"
    LOOKUP = "lookup"
    JSON = "json"
    UNKNOWN = "unknown"


class SchemaDefinition(Base):
    """Schema definition for a data model."""
    
    __tablename__ = "schema_definitions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    file_id: Mapped[int | None] = mapped_column(ForeignKey("source_files.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_type: Mapped[SchemaType] = mapped_column(Enum(SchemaType), nullable=False)
    system_type: Mapped[str] = mapped_column(String(100), nullable=False)  # zoho, odoo, csv, etc.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    project = relationship("Project", back_populates="schemas")
    fields = relationship("FieldDefinition", back_populates="schema", cascade="all, delete-orphan")


class FieldDefinition(Base):
    """Field definition within a schema."""
    
    __tablename__ = "field_definitions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schema_id: Mapped[int] = mapped_column(ForeignKey("schema_definitions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    field_type: Mapped[FieldType] = mapped_column(Enum(FieldType), default=FieldType.STRING)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    is_primary_key: Mapped[bool] = mapped_column(Boolean, default=False)
    is_lookup: Mapped[bool] = mapped_column(Boolean, default=False)
    unique_values_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sample_values: Mapped[list | None] = mapped_column(JSON, nullable=True)
    validation_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    schema = relationship("SchemaDefinition", back_populates="fields")
