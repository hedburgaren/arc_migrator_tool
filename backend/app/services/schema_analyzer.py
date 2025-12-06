"""
Schema analysis service for CSV/XLSX files.
"""
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import chardet
from datetime import datetime

logger = logging.getLogger(__name__)


class SchemaAnalyzer:
    """Service for analyzing file schemas and inferring data types."""
    
    def __init__(self, sample_size: int = 5):
        """
        Initialize schema analyzer.
        
        Args:
            sample_size: Number of sample values to extract per column
        """
        self.sample_size = sample_size
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(100000)  # Read first 100KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.info(f"Detected encoding: {encoding} (confidence: {confidence})")
                
                # Fallback to utf-8 if confidence is low
                if confidence < 0.7:
                    logger.warning(f"Low confidence ({confidence}), using utf-8 as fallback")
                    return 'utf-8'
                
                return encoding or 'utf-8'
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}, using utf-8")
            return 'utf-8'
    
    def read_file(
        self,
        file_path: str,
        encoding: Optional[str] = None,
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None
    ) -> Tuple[pd.DataFrame, str]:
        """
        Read CSV or XLSX file into DataFrame.
        
        Args:
            file_path: Path to the file
            encoding: Optional encoding (will be detected if not provided)
            sheet_name: Optional sheet name for Excel files
            sheet_index: Optional sheet index for Excel files
            
        Returns:
            Tuple of (DataFrame, detected_encoding)
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            if encoding is None:
                encoding = self.detect_encoding(file_path)
            
            try:
                # Try to read with detected encoding
                df = pd.read_csv(file_path, encoding=encoding)
                return df, encoding
            except Exception as e:
                logger.warning(f"Failed to read with encoding {encoding}: {e}")
                # Try common encodings as fallback
                for fallback_encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=fallback_encoding)
                        logger.info(f"Successfully read with fallback encoding: {fallback_encoding}")
                        return df, fallback_encoding
                    except Exception:
                        continue
                raise ValueError(f"Could not read CSV file with any supported encoding")
        
        elif file_ext in ['.xlsx', '.xls']:
            # Import ExcelService for multi-sheet support
            from app.services.excel_service import ExcelService
            excel_service = ExcelService()
            
            # Use ExcelService for advanced multi-sheet support
            df, metadata = excel_service.read_excel_file(file_path, sheet_name, sheet_index)
            return df, 'n/a'
        
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def infer_data_type(self, series: pd.Series) -> str:
        """
        Infer data type for a pandas Series.
        
        Args:
            series: Pandas Series to analyze
            
        Returns:
            Inferred data type string
        """
        # Remove null values for type detection
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return "null"
        
        # Check pandas dtype
        dtype = series.dtype
        
        # Check for boolean
        if dtype == 'bool':
            return "boolean"
        
        # Check for integer
        if pd.api.types.is_integer_dtype(dtype):
            return "integer"
        
        # Check for float
        if pd.api.types.is_float_dtype(dtype):
            return "float"
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "date"
        
        # For object dtype, try to infer more specific type
        if dtype == 'object':
            # Try to convert to datetime
            try:
                pd.to_datetime(non_null.head(100))
                return "date"
            except (ValueError, TypeError):
                pass
            
            # Try to convert to numeric
            try:
                converted = pd.to_numeric(non_null.head(100))
                if (converted % 1 == 0).all():
                    return "integer"
                else:
                    return "float"
            except (ValueError, TypeError):
                pass
            
            # Check if boolean-like
            unique_values = non_null.unique()
            if len(unique_values) <= 2:
                bool_like = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
                if all(str(v).lower() in bool_like for v in unique_values):
                    return "boolean"
            
            return "string"
        
        # Default to string for unknown types
        return "string"
    
    def get_sample_values(self, series: pd.Series, n: int = 5) -> List[Any]:
        """
        Extract sample non-null values from a series.
        
        Args:
            series: Pandas Series to sample
            n: Number of samples to extract
            
        Returns:
            List of sample values
        """
        non_null = series.dropna()
        samples = non_null.head(n).tolist()
        
        # Convert to JSON-serializable types
        result = []
        for val in samples:
            if pd.isna(val):
                continue
            elif isinstance(val, (pd.Timestamp, datetime)):
                result.append(val.isoformat())
            elif isinstance(val, (int, float, str, bool)):
                result.append(val)
            else:
                result.append(str(val))
        
        return result
    
    def calculate_statistics(self, series: pd.Series, data_type: str) -> Optional[Dict[str, Any]]:
        """
        Calculate statistics for numeric columns.
        
        Args:
            series: Pandas Series to analyze
            data_type: Inferred data type
            
        Returns:
            Dictionary with statistics or None for non-numeric types
        """
        if data_type in ['integer', 'float']:
            non_null = series.dropna()
            if len(non_null) > 0:
                return {
                    'min': float(non_null.min()),
                    'max': float(non_null.max()),
                    'mean': float(non_null.mean()),
                    'median': float(non_null.median()),
                    'std': float(non_null.std()) if len(non_null) > 1 else 0.0
                }
        return None
    
    def analyze_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Analyze DataFrame and extract schema information.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of column metadata dictionaries
        """
        columns_metadata = []
        
        for idx, col_name in enumerate(df.columns):
            series = df[col_name]
            
            # Infer data type
            data_type = self.infer_data_type(series)
            
            # Get sample values
            sample_values = self.get_sample_values(series, self.sample_size)
            
            # Calculate null and unique counts
            null_count = int(series.isna().sum())
            unique_count = int(series.nunique())
            
            # Calculate statistics for numeric columns
            statistics = self.calculate_statistics(series, data_type)
            
            columns_metadata.append({
                'column_name': str(col_name),
                'column_index': idx,
                'data_type': data_type,
                'sample_values': sample_values,
                'null_count': null_count,
                'unique_count': unique_count,
                'statistics': statistics
            })
        
        return columns_metadata
    
    def analyze_file(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze a file and return complete schema information.
        
        Args:
            file_path: Path to the file to analyze
            sheet_name: Optional sheet name for Excel files
            sheet_index: Optional sheet index for Excel files
            
        Returns:
            Dictionary with schema information
        """
        # Check if Excel file for metadata
        file_ext = os.path.splitext(file_path)[1].lower()
        excel_metadata = None
        
        if file_ext in ['.xlsx', '.xls']:
            from app.services.excel_service import ExcelService
            excel_service = ExcelService()
            excel_metadata = excel_service.extract_excel_metadata(file_path)
        
        # Read file
        df, encoding = self.read_file(file_path, sheet_name=sheet_name, sheet_index=sheet_index)
        
        # Analyze columns
        columns_metadata = self.analyze_dataframe(df)
        
        result = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'encoding': encoding,
            'columns': columns_metadata
        }
        
        # Add Excel metadata if available
        if excel_metadata:
            result['excel_metadata'] = excel_metadata
        
        return result
