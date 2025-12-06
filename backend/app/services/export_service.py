"""
Export service for generating output files from transformed data.
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import uuid

logger = logging.getLogger(__name__)

# Configure export directory
EXPORT_DIR = "./data/exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


class ExportService:
    """Service for generating export files from transformed data."""
    
    def __init__(self):
        """Initialize export service."""
        self.export_dir = EXPORT_DIR
    
    def generate_csv(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate CSV file from DataFrame.
        
        Args:
            data: DataFrame to export
            filename: Optional custom filename (without extension)
            options: Export options (encoding, delimiter, etc.)
            
        Returns:
            Path to generated CSV file
        """
        options = options or {}
        
        # Generate filename if not provided
        if not filename:
            filename = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename = f"{filename}.csv"
        
        file_path = os.path.join(self.export_dir, filename)
        
        # Get export options
        encoding = options.get('encoding', 'utf-8')
        delimiter = options.get('delimiter', ',')
        index = options.get('include_index', False)
        
        try:
            # Export to CSV
            data.to_csv(
                file_path,
                index=index,
                encoding=encoding,
                sep=delimiter
            )
            
            logger.info(f"Generated CSV export: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to generate CSV: {str(e)}")
            raise
    
    def generate_xlsx(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate XLSX file from DataFrame.
        
        Args:
            data: DataFrame to export
            filename: Optional custom filename (without extension)
            options: Export options (sheet_name, etc.)
            
        Returns:
            Path to generated XLSX file
        """
        options = options or {}
        
        # Generate filename if not provided
        if not filename:
            filename = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename = f"{filename}.xlsx"
        
        file_path = os.path.join(self.export_dir, filename)
        
        # Get export options
        sheet_name = options.get('sheet_name', 'Sheet1')
        index = options.get('include_index', False)
        
        try:
            # Export to Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                data.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=index
                )
            
            logger.info(f"Generated XLSX export: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to generate XLSX: {str(e)}")
            raise
    
    def generate_export(
        self,
        data: pd.DataFrame,
        format: str = "csv",
        filename: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate export file in specified format.
        
        Args:
            data: DataFrame to export
            format: Export format ('csv' or 'xlsx')
            filename: Optional custom filename (without extension)
            options: Format-specific export options
            
        Returns:
            Path to generated file
        """
        if format.lower() == "csv":
            return self.generate_csv(data, filename, options)
        elif format.lower() == "xlsx":
            return self.generate_xlsx(data, filename, options)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_expired_exports(self, expiration_hours: int = 24):
        """
        Clean up expired export files.
        
        Args:
            expiration_hours: Files older than this will be deleted
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=expiration_hours)
            
            for filename in os.listdir(self.export_dir):
                file_path = os.path.join(self.export_dir, filename)
                
                # Skip if not a file
                if not os.path.isfile(file_path):
                    continue
                
                # Check file age
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted expired export: {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {filename}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Export cleanup failed: {str(e)}")
    
    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
