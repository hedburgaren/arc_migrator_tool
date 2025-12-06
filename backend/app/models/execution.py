"""Execution run and log models."""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ExecutionMode(str, enum.Enum):
    """Execution mode enumeration."""
    PREVIEW = "preview"
    DRY_RUN = "dry_run"
    COMMIT = "commit"


class ExecutionStatus(str, enum.Enum):
    """Execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(str, enum.Enum):
    """Log level enumeration."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ExecutionRun(Base):
    """Execution run record."""
    
    __tablename__ = "execution_runs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    mapping_profile_id: Mapped[int] = mapped_column(ForeignKey("mapping_profiles.id"), nullable=False)
    mode: Mapped[ExecutionMode] = mapped_column(Enum(ExecutionMode), nullable=False)
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus),
        default=ExecutionStatus.PENDING
    )
    total_records: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processed_records: Mapped[int] = mapped_column(Integer, default=0)
    successful_records: Mapped[int] = mapped_column(Integer, default=0)
    failed_records: Mapped[int] = mapped_column(Integer, default=0)
    warnings_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_files: Mapped[list | None] = mapped_column(JSON, nullable=True)  # List of output file paths
    rollback_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Rollback information
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    project = relationship("Project", back_populates="executions")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")


class ExecutionLog(Base):
    """Execution log entry."""
    
    __tablename__ = "execution_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(ForeignKey("execution_runs.id"), nullable=False)
    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), default=LogLevel.INFO)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    record_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    field_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    execution = relationship("ExecutionRun", back_populates="logs")
