"""
Schema model for storing column metadata from analyzed files.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Schema(Base):
    """Schema model for tracking column metadata."""
    
    __tablename__ = "schemas"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    column_name = Column(String, nullable=False)
    column_index = Column(Integer, nullable=False)
    data_type = Column(String, nullable=False)  # string, integer, float, date, boolean, mixed
    sample_values = Column(JSON, nullable=True)  # List of sample values
    null_count = Column(Integer, default=0, nullable=False)
    unique_count = Column(Integer, default=0, nullable=False)
    statistics = Column(JSON, nullable=True)  # Dict with min, max, avg for numbers
    
    # Relationship to file
    file = relationship("File", back_populates="schemas")
    
    def __repr__(self):
        return f"<Schema(id={self.id}, file_id={self.file_id}, column='{self.column_name}')>"
