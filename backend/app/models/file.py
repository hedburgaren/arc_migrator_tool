"""
File model for storing uploaded file metadata.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, func
from app.core.database import Base


class File(Base):
    """File model for tracking uploaded files."""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    status = Column(String, default="uploaded", nullable=False)  # uploaded, processing, error
    
    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', status='{self.status}')>"
