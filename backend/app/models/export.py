"""
Export model for storing generated export files.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base


class Export(Base):
    """Export model for tracking generated export files."""
    
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    format = Column(String(10), nullable=False)  # 'csv', 'xlsx'
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default="generating", nullable=False)  # generating, ready, expired, error
    records_exported = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationship to project
    project = relationship("Project", back_populates="exports")
    
    def __repr__(self):
        return f"<Export(id={self.id}, project_id={self.project_id}, format='{self.format}', status='{self.status}')>"
