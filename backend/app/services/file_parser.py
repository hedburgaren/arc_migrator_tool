"""Universal file parser with encoding detection and validation."""

import logging
from pathlib import Path
from typing import BinaryIO

import chardet
import pandas as pd

logger = logging.getLogger(__name__)


class FileParserError(Exception):
    """Exception raised for file parsing errors."""
    pass


class FileParser:
    """Universal file parser supporting CSV, Excel, and JSON formats."""
    
    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json'}
    
    @staticmethod
    def detect_encoding(file_content: bytes) -> str:
        """Detect file encoding using chardet."""
        result = chardet.detect(file_content)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)
        
        logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
        
        # Fall back to utf-8 if detection is uncertain
        if confidence < 0.5 or encoding is None:
            encoding = 'utf-8'
        
        return encoding
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """Get file type from filename extension."""
        ext = Path(filename).suffix.lower()
        if ext in {'.csv'}:
            return 'csv'
        elif ext in {'.xlsx', '.xls'}:
            return 'xlsx'
        elif ext in {'.json'}:
            return 'json'
        else:
            raise FileParserError(f"Unsupported file type: {ext}")
    
    @classmethod
    def validate_file(cls, filename: str, file_size: int) -> None:
        """Validate file before processing."""
        ext = Path(filename).suffix.lower()
        
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise FileParserError(
                f"Unsupported file format: {ext}. "
                f"Supported formats: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
            )
        
        # Check file size (max 100MB)
        max_size = 100 * 1024 * 1024
        if file_size > max_size:
            raise FileParserError(
                f"File too large: {file_size / (1024*1024):.1f}MB. "
                f"Maximum allowed: {max_size / (1024*1024):.0f}MB"
            )
    
    @classmethod
    def parse_csv(
        cls,
        file_path: str | Path,
        encoding: str | None = None,
        delimiter: str | None = None
    ) -> pd.DataFrame:
        """Parse a CSV file into a DataFrame."""
        file_path = Path(file_path)
        
        # Read file content for encoding detection if not provided
        if encoding is None:
            with open(file_path, 'rb') as f:
                content = f.read(10000)  # Read first 10KB for detection
                encoding = cls.detect_encoding(content)
        
        # Try common delimiters if not specified
        delimiters = [delimiter] if delimiter else [',', ';', '\t', '|']
        
        last_error = None
        for delim in delimiters:
            try:
                df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    delimiter=delim,
                    dtype=str,  # Read all as string initially
                    na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                    keep_default_na=True,
                    low_memory=False
                )
                
                # Check if we got reasonable columns (more than 1 usually means correct delimiter)
                if len(df.columns) > 1 or delimiter is not None:
                    logger.info(f"Successfully parsed CSV with delimiter '{delim}', {len(df)} rows, {len(df.columns)} columns")
                    return df
                    
            except Exception as e:
                last_error = e
                continue
        
        # If all delimiters failed, raise error
        raise FileParserError(f"Failed to parse CSV file: {last_error}")
    
    @classmethod
    def parse_excel(
        cls,
        file_path: str | Path,
        sheet_name: str | int | None = 0
    ) -> tuple[pd.DataFrame, str]:
        """Parse an Excel file into a DataFrame."""
        file_path = Path(file_path)
        
        try:
            # Get sheet names
            xl = pd.ExcelFile(file_path)
            sheet_names = xl.sheet_names
            
            if isinstance(sheet_name, str) and sheet_name not in sheet_names:
                raise FileParserError(
                    f"Sheet '{sheet_name}' not found. Available sheets: {sheet_names}"
                )
            
            actual_sheet = sheet_names[sheet_name] if isinstance(sheet_name, int) else sheet_name
            
            df = pd.read_excel(
                file_path,
                sheet_name=actual_sheet,
                dtype=str,
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True
            )
            
            logger.info(f"Successfully parsed Excel sheet '{actual_sheet}', {len(df)} rows, {len(df.columns)} columns")
            return df, actual_sheet
            
        except FileParserError:
            raise
        except Exception as e:
            raise FileParserError(f"Failed to parse Excel file: {e}")
    
    @classmethod
    def parse_json(cls, file_path: str | Path) -> pd.DataFrame:
        """Parse a JSON file into a DataFrame."""
        file_path = Path(file_path)
        
        try:
            # Try different JSON formats
            try:
                df = pd.read_json(file_path, dtype=str)
            except ValueError:
                # Try reading as line-delimited JSON
                df = pd.read_json(file_path, lines=True, dtype=str)
            
            logger.info(f"Successfully parsed JSON, {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            raise FileParserError(f"Failed to parse JSON file: {e}")
    
    @classmethod
    def parse_file(
        cls,
        file_path: str | Path,
        file_type: str | None = None,
        **kwargs
    ) -> tuple[pd.DataFrame, dict]:
        """
        Parse a file into a DataFrame with metadata.
        
        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        file_path = Path(file_path)
        
        if file_type is None:
            file_type = cls.get_file_type(file_path.name)
        
        metadata = {
            'file_type': file_type,
            'encoding': None,
            'sheet_name': None,
            'row_count': 0,
            'column_count': 0,
            'columns': []
        }
        
        if file_type == 'csv':
            encoding = kwargs.get('encoding')
            if encoding is None:
                with open(file_path, 'rb') as f:
                    content = f.read(10000)
                    encoding = cls.detect_encoding(content)
            
            df = cls.parse_csv(file_path, encoding=encoding, delimiter=kwargs.get('delimiter'))
            metadata['encoding'] = encoding
            
        elif file_type in {'xlsx', 'xls'}:
            sheet_name = kwargs.get('sheet_name', 0)
            df, actual_sheet = cls.parse_excel(file_path, sheet_name=sheet_name)
            metadata['sheet_name'] = actual_sheet
            
        elif file_type == 'json':
            df = cls.parse_json(file_path)
            
        else:
            raise FileParserError(f"Unsupported file type: {file_type}")
        
        metadata['row_count'] = len(df)
        metadata['column_count'] = len(df.columns)
        metadata['columns'] = list(df.columns)
        
        return df, metadata
    
    @classmethod
    def get_preview(cls, df: pd.DataFrame, rows: int = 100) -> list[dict]:
        """Get preview data from DataFrame."""
        return df.head(rows).to_dict(orient='records')
    
    @classmethod
    def get_excel_sheets(cls, file_path: str | Path) -> list[str]:
        """Get list of sheet names from an Excel file."""
        try:
            xl = pd.ExcelFile(file_path)
            return xl.sheet_names
        except Exception as e:
            raise FileParserError(f"Failed to read Excel file: {e}")
