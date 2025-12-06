"""
File validation service for validating uploaded files.
"""
import os
import logging
from typing import List, Dict, Any, Tuple
import pandas as pd
import chardet

logger = logging.getLogger(__name__)


class FileValidator:
    """Service for validating uploaded files."""
    
    def __init__(self):
        """Initialize file validator."""
        pass
    
    def validate_file(
        self,
        file_path: str,
        check_encoding: bool = True,
        check_structure: bool = True,
        check_data_quality: bool = True,
        max_file_size_mb: int = 100
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Validate an uploaded file.
        
        Args:
            file_path: Path to file
            check_encoding: Whether to check encoding
            check_structure: Whether to check structure
            check_data_quality: Whether to check data quality
            max_file_size_mb: Maximum file size in MB
            
        Returns:
            Tuple of (status, list_of_issues)
            Status is one of: 'passed', 'warning', 'failed'
        """
        issues = []
        
        # Check if file exists
        if not os.path.exists(file_path):
            return 'failed', [{
                'severity': 'error',
                'message': 'File not found',
                'field': None,
                'details': {'path': file_path}
            }]
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_file_size_mb:
            issues.append({
                'severity': 'error',
                'message': f'File size ({file_size_mb:.2f} MB) exceeds maximum ({max_file_size_mb} MB)',
                'field': None,
                'details': {'size_mb': file_size_mb, 'max_size_mb': max_file_size_mb}
            })
        
        # Check file format
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.csv', '.xlsx', '.xls']:
            issues.append({
                'severity': 'error',
                'message': f'Unsupported file format: {file_ext}',
                'field': None,
                'details': {'extension': file_ext}
            })
            return 'failed', issues
        
        # Check encoding (CSV only)
        if check_encoding and file_ext == '.csv':
            encoding_issues = self._check_encoding(file_path)
            issues.extend(encoding_issues)
        
        # Check structure and data quality
        try:
            if file_ext == '.csv':
                # Detect encoding
                with open(file_path, 'rb') as f:
                    raw_data = f.read(100000)
                    result = chardet.detect(raw_data)
                    encoding = result['encoding'] or 'utf-8'
                
                df = pd.read_csv(file_path, encoding=encoding)
            else:
                df = pd.read_excel(file_path)
            
            # Check structure
            if check_structure:
                structure_issues = self._check_structure(df)
                issues.extend(structure_issues)
            
            # Check data quality
            if check_data_quality:
                quality_issues = self._check_data_quality(df)
                issues.extend(quality_issues)
                
        except Exception as e:
            issues.append({
                'severity': 'error',
                'message': f'Failed to read file: {str(e)}',
                'field': None,
                'details': {'error': str(e)}
            })
            return 'failed', issues
        
        # Determine overall status
        has_errors = any(issue['severity'] == 'error' for issue in issues)
        has_warnings = any(issue['severity'] == 'warning' for issue in issues)
        
        if has_errors:
            return 'failed', issues
        elif has_warnings:
            return 'warning', issues
        else:
            return 'passed', issues
    
    def _check_encoding(self, file_path: str) -> List[Dict[str, Any]]:
        """Check file encoding."""
        issues = []
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(100000)
                result = chardet.detect(raw_data)
                
                if result['confidence'] < 0.7:
                    issues.append({
                        'severity': 'warning',
                        'message': f"Low confidence in encoding detection ({result['confidence']:.2f})",
                        'field': None,
                        'details': {'encoding': result['encoding'], 'confidence': result['confidence']}
                    })
        except Exception as e:
            issues.append({
                'severity': 'error',
                'message': f'Encoding detection failed: {str(e)}',
                'field': None,
                'details': {'error': str(e)}
            })
        
        return issues
    
    def _check_structure(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check file structure."""
        issues = []
        
        # Check if DataFrame is empty
        if df.empty:
            issues.append({
                'severity': 'error',
                'message': 'File contains no data rows',
                'field': None,
                'details': {}
            })
            return issues
        
        # Check for empty column names
        empty_cols = [col for col in df.columns if not str(col).strip() or str(col) == 'Unnamed']
        if empty_cols:
            issues.append({
                'severity': 'warning',
                'message': f'Found {len(empty_cols)} columns with empty or unnamed headers',
                'field': None,
                'details': {'columns': empty_cols}
            })
        
        # Check for duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            issues.append({
                'severity': 'error',
                'message': f'Found duplicate column names',
                'field': None,
                'details': {'duplicates': duplicate_cols}
            })
        
        # Check for very wide files (>100 columns)
        if len(df.columns) > 100:
            issues.append({
                'severity': 'warning',
                'message': f'File has {len(df.columns)} columns (very wide)',
                'field': None,
                'details': {'column_count': len(df.columns)}
            })
        
        return issues
    
    def _check_data_quality(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check data quality."""
        issues = []
        
        # Check for columns with all null values
        all_null_cols = [col for col in df.columns if df[col].isna().all()]
        if all_null_cols:
            issues.append({
                'severity': 'warning',
                'message': f'Found {len(all_null_cols)} columns with all null values',
                'field': None,
                'details': {'columns': all_null_cols}
            })
        
        # Check for rows with all null values
        all_null_rows = df[df.isna().all(axis=1)].index.tolist()
        if all_null_rows:
            issues.append({
                'severity': 'warning',
                'message': f'Found {len(all_null_rows)} rows with all null values',
                'field': None,
                'details': {'row_count': len(all_null_rows)}
            })
        
        # Check for high null percentage in columns
        for col in df.columns:
            null_pct = (df[col].isna().sum() / len(df)) * 100
            if null_pct > 50:
                issues.append({
                    'severity': 'warning',
                    'message': f"Column '{col}' has {null_pct:.1f}% null values",
                    'field': col,
                    'details': {'null_percentage': null_pct}
                })
        
        return issues
