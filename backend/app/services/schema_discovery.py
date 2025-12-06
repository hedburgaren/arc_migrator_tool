"""Schema discovery service for analyzing data structures."""

import logging
import re
from datetime import datetime
from typing import Any

import pandas as pd
from dateutil import parser as date_parser

from app.models.schema import FieldType

logger = logging.getLogger(__name__)


class SchemaDiscoveryService:
    """Service for discovering and analyzing data schemas."""
    
    # Thresholds for lookup detection
    LOOKUP_MAX_UNIQUE_VALUES = 50
    LOOKUP_MAX_UNIQUE_RATIO = 0.1  # Max 10% unique values
    
    # Common date patterns
    DATE_PATTERNS = [
        r'^\d{4}-\d{2}-\d{2}$',  # ISO date
        r'^\d{2}/\d{2}/\d{4}$',  # US date
        r'^\d{2}-\d{2}-\d{4}$',  # EU date
        r'^\d{4}/\d{2}/\d{2}$',  # Alternative ISO
    ]
    
    DATETIME_PATTERNS = [
        r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',  # ISO datetime
        r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}',  # US datetime
    ]
    
    @classmethod
    def infer_field_type(cls, values: pd.Series) -> FieldType:
        """Infer the data type of a field from its values."""
        # Drop nulls for analysis
        non_null = values.dropna()
        
        if len(non_null) == 0:
            return FieldType.STRING
        
        # Sample values for analysis (max 1000)
        sample = non_null.head(1000)
        
        # Check for boolean
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
        if all(str(v).lower().strip() in bool_values for v in sample):
            return FieldType.BOOLEAN
        
        # Check for integer
        try:
            int_vals = pd.to_numeric(sample, errors='raise')
            if all(int_vals == int_vals.astype(int)):
                return FieldType.INTEGER
            return FieldType.FLOAT
        except (ValueError, TypeError):
            pass
        
        # Check for date/datetime
        date_count = 0
        datetime_count = 0
        for val in sample.head(100):
            val_str = str(val).strip()
            
            # Check date patterns
            for pattern in cls.DATE_PATTERNS:
                if re.match(pattern, val_str):
                    date_count += 1
                    break
            
            # Check datetime patterns
            for pattern in cls.DATETIME_PATTERNS:
                if re.match(pattern, val_str):
                    datetime_count += 1
                    break
        
        sample_size = min(100, len(sample))
        if datetime_count > sample_size * 0.8:
            return FieldType.DATETIME
        if date_count > sample_size * 0.8:
            return FieldType.DATE
        
        # Try parsing as dates
        try:
            parsed_count = 0
            for val in sample.head(50):
                try:
                    date_parser.parse(str(val))
                    parsed_count += 1
                except (ValueError, TypeError):
                    pass
            
            if parsed_count > 40:  # 80% success rate
                return FieldType.DATE
        except Exception:
            pass
        
        # Default to string
        return FieldType.STRING
    
    @classmethod
    def is_lookup_candidate(cls, values: pd.Series, total_rows: int) -> bool:
        """Determine if a field is a lookup candidate based on unique values."""
        non_null = values.dropna()
        
        if len(non_null) == 0:
            return False
        
        unique_count = non_null.nunique()
        unique_ratio = unique_count / total_rows if total_rows > 0 else 1
        
        # Lookup if few unique values AND low ratio
        return (
            unique_count <= cls.LOOKUP_MAX_UNIQUE_VALUES and 
            unique_ratio <= cls.LOOKUP_MAX_UNIQUE_RATIO
        )
    
    @classmethod
    def analyze_field(cls, name: str, values: pd.Series, position: int) -> dict[str, Any]:
        """Analyze a single field and return its metadata."""
        total_rows = len(values)
        non_null = values.dropna()
        non_null_count = len(non_null)
        
        # Infer type
        field_type = cls.infer_field_type(values)
        
        # Check if lookup candidate
        is_lookup = cls.is_lookup_candidate(values, total_rows)
        
        # Get unique values count and samples
        unique_count = non_null.nunique()
        
        # Get sample values (up to 10 unique values)
        sample_values = []
        if unique_count > 0:
            sample_values = [str(v) for v in non_null.unique()[:10].tolist()]
        
        # Detect if likely required (has values in most rows)
        null_ratio = (total_rows - non_null_count) / total_rows if total_rows > 0 else 0
        is_required = null_ratio < 0.05  # Less than 5% nulls
        
        # Check if might be primary key
        is_primary_key = (
            unique_count == non_null_count == total_rows and 
            total_rows > 0 and
            field_type in {FieldType.STRING, FieldType.INTEGER}
        )
        
        return {
            'name': name,
            'display_name': cls.humanize_field_name(name),
            'field_type': field_type,
            'is_required': is_required,
            'is_primary_key': is_primary_key,
            'is_lookup': is_lookup,
            'unique_values_count': unique_count,
            'sample_values': sample_values,
            'null_count': total_rows - non_null_count,
            'position': position,
            'metadata_json': {
                'total_rows': total_rows,
                'non_null_count': non_null_count,
                'null_ratio': null_ratio,
            }
        }
    
    @classmethod
    def humanize_field_name(cls, name: str) -> str:
        """Convert field name to human-readable format."""
        # Handle camelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        # Handle snake_case
        name = name.replace('_', ' ')
        # Handle kebab-case
        name = name.replace('-', ' ')
        # Capitalize words
        return ' '.join(word.capitalize() for word in name.split())
    
    @classmethod
    def discover_schema(cls, df: pd.DataFrame, schema_name: str) -> dict[str, Any]:
        """
        Discover schema from a DataFrame.
        
        Returns:
            Dict with schema info and list of field definitions
        """
        fields = []
        
        for position, column in enumerate(df.columns):
            field_info = cls.analyze_field(column, df[column], position)
            fields.append(field_info)
        
        return {
            'name': schema_name,
            'row_count': len(df),
            'column_count': len(df.columns),
            'fields': fields,
            'lookup_candidates': [f for f in fields if f['is_lookup']],
            'primary_key_candidates': [f for f in fields if f['is_primary_key']],
        }
    
    @classmethod
    def get_field_statistics(cls, values: pd.Series) -> dict[str, Any]:
        """Get detailed statistics for a field."""
        non_null = values.dropna()
        
        stats = {
            'total_count': len(values),
            'non_null_count': len(non_null),
            'null_count': len(values) - len(non_null),
            'unique_count': non_null.nunique(),
        }
        
        # Try numeric statistics
        try:
            numeric = pd.to_numeric(non_null, errors='raise')
            stats.update({
                'min': float(numeric.min()),
                'max': float(numeric.max()),
                'mean': float(numeric.mean()),
                'median': float(numeric.median()),
            })
        except (ValueError, TypeError):
            pass
        
        # String statistics
        if non_null.dtype == object:
            str_lengths = non_null.astype(str).str.len()
            stats.update({
                'min_length': int(str_lengths.min()),
                'max_length': int(str_lengths.max()),
                'avg_length': float(str_lengths.mean()),
            })
        
        return stats
