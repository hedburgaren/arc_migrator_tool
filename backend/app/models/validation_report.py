"""
ValidationReport model for storing validation results.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class ValidationReport(Base):
    """ValidationReport model for tracking validation results."""
    
    __tablename__ = "validation_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=True, index=True)
    validation_type = Column(String(50), nullable=False)  # 'file', 'mapping', 'data'
    status = Column(String(50), nullable=False)  # 'passed', 'warning', 'failed'
    issues = Column(JSON, nullable=True)  # Array of validation issues
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="validation_reports")
    file = relationship("File", back_populates="validation_reports")
    
    def __repr__(self):
        return f"<ValidationReport(id={self.id}, type='{self.validation_type}', status='{self.status}')>"
