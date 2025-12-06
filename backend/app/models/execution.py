"""
Execution model for storing migration execution history.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Execution(Base):
    """Execution model for tracking migration runs."""
    
    __tablename__ = "executions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    execution_type = Column(String(50), nullable=False)  # preview, dry_run, commit
    status = Column(String(50), default="pending", nullable=False)  # pending, running, completed, failed
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    records_processed = Column(Integer, default=0, nullable=False)
    records_successful = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    execution_log = Column(JSON, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Relationship to project
    project = relationship("Project", back_populates="executions")
    
    def __repr__(self):
        return f"<Execution(id={self.id}, project_id={self.project_id}, type='{self.execution_type}', status='{self.status}')>"
