"""CSV/XLSX connector for file-based data operations."""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from app.connectors.base import ConnectorBase, ConnectorRegistry
from app.services.file_parser import FileParser, FileParserError


class CSVXLSXConnector(ConnectorBase):
    """Connector for CSV and XLSX file operations."""
    
    name = "csv_xlsx"
    display_name = "CSV/Excel Files"
    description = "Read and write CSV and Excel files with encoding detection and format support"
    version = "1.0.0"
    supported_modes = ["read", "write"]
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize connector with configuration."""
        super().__init__(config)
        self.file_path: Optional[Path] = None
        self.dataframe: Optional[pd.DataFrame] = None
    
    async def connect(self) -> bool:
        """Validate file path if provided."""
        file_path = self.config.get("file_path")
        
        if file_path:
            self.file_path = Path(file_path)
            if not self.file_path.exists():
                return False
        
        self._connected = True
        return True
    
    async def disconnect(self) -> None:
        """Release resources."""
        self.dataframe = None
        self.file_path = None
        self._connected = False
    
    async def get_schema(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Discover schema from file.
        
        For CSV/XLSX, the schema is discovered by analyzing the file content.
        """
        if not self.file_path or not self.file_path.exists():
            return {
                "models": [],
                "message": "No file configured. Use file upload for CSV schema discovery."
            }
        
        try:
            df, metadata = FileParser.parse_file(self.file_path)
            
            fields = []
            for col in df.columns:
                fields.append({
                    "name": col,
                    "type": str(df[col].dtype),
                    "nullable": df[col].isnull().any(),
                    "unique_count": df[col].nunique(),
                })
            
            return {
                "models": [{
                    "name": model_name or self.file_path.stem,
                    "fields": fields,
                    "row_count": len(df),
                }],
                "metadata": metadata,
            }
        except FileParserError as e:
            return {"models": [], "error": str(e)}
    
    async def extract(
        self,
        model_name: str,
        filters: Dict[str, Any] = None,
        limit: int = None
    ) -> pd.DataFrame:
        """
        Extract data from file.
        
        Args:
            model_name: Ignored for file operations
            filters: Optional dict of column -> value filters
            limit: Maximum records to return
            
        Returns:
            DataFrame with file contents
        """
        if not self.file_path or not self.file_path.exists():
            return pd.DataFrame()
        
        try:
            df, _ = FileParser.parse_file(
                self.file_path,
                sheet_name=self.config.get("sheet_name")
            )
            
            # Apply filters
            if filters:
                for column, value in filters.items():
                    if column in df.columns:
                        df = df[df[column] == value]
            
            # Apply limit
            if limit:
                df = df.head(limit)
            
            self.dataframe = df
            return df
        except FileParserError:
            return pd.DataFrame()
    
    async def push(
        self,
        model_name: str,
        data: pd.DataFrame,
        mode: str = "create"
    ) -> Dict[str, Any]:
        """
        Write data to file.
        
        Args:
            model_name: Used as filename if output_path not configured
            data: DataFrame to write
            mode: 'create' for new file, 'append' to add to existing
            
        Returns:
            Dict with operation results
        """
        output_path = self.config.get("output_path")
        output_format = self.config.get("output_format", "csv")
        
        if not output_path:
            output_path = f"{model_name}.{output_format}"
        
        output_path = Path(output_path)
        
        try:
            if output_format in {"csv", "txt"}:
                if mode == "append" and output_path.exists():
                    data.to_csv(output_path, mode="a", header=False, index=False)
                else:
                    data.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
            
            elif output_format in {"xlsx", "xls"}:
                sheet_name = self.config.get("sheet_name", "Sheet1")
                data.to_excel(output_path, index=False, sheet_name=sheet_name)
            
            elif output_format == "json":
                data.to_json(output_path, orient="records", indent=2)
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported output format: {output_format}"
                }
            
            return {
                "success": True,
                "file_path": str(output_path),
                "records_written": len(data),
                "format": output_format,
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_config(self) -> List[str]:
        """Validate connector configuration."""
        errors = []
        
        file_path = self.config.get("file_path")
        if file_path:
            path = Path(file_path)
            if not path.exists():
                errors.append(f"File not found: {file_path}")
            elif path.suffix.lower() not in {".csv", ".xlsx", ".xls", ".json"}:
                errors.append(f"Unsupported file type: {path.suffix}")
        
        output_format = self.config.get("output_format", "csv")
        if output_format not in {"csv", "xlsx", "xls", "json", "txt"}:
            errors.append(f"Unsupported output format: {output_format}")
        
        return errors


# Register the connector
ConnectorRegistry.register(CSVXLSXConnector)
