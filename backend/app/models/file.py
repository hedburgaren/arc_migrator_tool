"""
File model for storing uploaded file metadata.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class File(Base):
    """File model for tracking uploaded files."""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    status = Column(String, default="uploaded", nullable=False)  # uploaded, processing, error
    
    # Schema analysis fields
    schema_analyzed = Column(Boolean, default=False, nullable=False)
    column_count = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    encoding = Column(String, nullable=True)
    
    # Relationships
    schemas = relationship("Schema", back_populates="file", cascade="all, delete-orphan")
    validation_reports = relationship("ValidationReport", back_populates="file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', status='{self.status}')>"
