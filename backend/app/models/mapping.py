"""
Mapping model for storing field transformation mappings.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Mapping(Base):
    """Mapping model for tracking field transformations."""
    
    __tablename__ = "mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    source_field = Column(String(255), nullable=False)
    target_field = Column(String(255), nullable=False)
    transform_type = Column(String(50), default="1:1", nullable=False)
    transform_config = Column(JSON, nullable=True)
    validation_rules = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow(), nullable=False)
    
    # Relationship to project
    project = relationship("Project", back_populates="mappings")
    
    def __repr__(self):
        return f"<Mapping(id={self.id}, project_id={self.project_id}, source='{self.source_field}', target='{self.target_field}')>"
