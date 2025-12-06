"""Mapping engine for applying field transformations."""

import logging
import re
from typing import Any, Callable

import pandas as pd
from dateutil import parser as date_parser

from app.models.mapping import MappingType, TransformType

logger = logging.getLogger(__name__)


class MappingEngineError(Exception):
    """Exception raised for mapping errors."""
    pass


class TransformFunctions:
    """Collection of transform functions."""
    
    @staticmethod
    def lowercase(value: Any) -> str:
        """Convert value to lowercase."""
        return str(value).lower() if value is not None else ''
    
    @staticmethod
    def uppercase(value: Any) -> str:
        """Convert value to uppercase."""
        return str(value).upper() if value is not None else ''
    
    @staticmethod
    def trim(value: Any) -> str:
        """Trim whitespace from value."""
        return str(value).strip() if value is not None else ''
    
    @staticmethod
    def concat(values: list[Any], separator: str = ' ') -> str:
        """Concatenate multiple values."""
        return separator.join(str(v) for v in values if v is not None and str(v).strip())
    
    @staticmethod
    def split(value: Any, separator: str = ',', index: int = 0) -> str:
        """Split value and return specified part."""
        if value is None:
            return ''
        parts = str(value).split(separator)
        if 0 <= index < len(parts):
            return parts[index].strip()
        return ''
    
    @staticmethod
    def replace(value: Any, old: str, new: str) -> str:
        """Replace substring in value."""
        if value is None:
            return ''
        return str(value).replace(old, new)
    
    @staticmethod
    def format_date(value: Any, output_format: str = '%Y-%m-%d') -> str:
        """Parse and format date value."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return ''
        try:
            parsed = date_parser.parse(str(value))
            return parsed.strftime(output_format)
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def to_number(value: Any, default: float = 0) -> float:
        """Convert value to number."""
        if value is None:
            return default
        try:
            # Remove common formatting
            clean = re.sub(r'[^\d.-]', '', str(value))
            return float(clean) if clean else default
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def to_string(value: Any) -> str:
        """Convert value to string."""
        if value is None:
            return ''
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)
    
    @staticmethod
    def lookup(value: Any, lookup_table: dict, default: str = '') -> str:
        """Look up value in mapping table."""
        if value is None:
            return default
        str_value = str(value).strip()
        return lookup_table.get(str_value, lookup_table.get(str_value.lower(), default))


class MappingEngine:
    """Engine for applying field mappings and transformations."""
    
    # Map transform types to functions
    TRANSFORM_FUNCTIONS: dict[TransformType, Callable] = {
        TransformType.LOWERCASE: TransformFunctions.lowercase,
        TransformType.UPPERCASE: TransformFunctions.uppercase,
        TransformType.TRIM: TransformFunctions.trim,
        TransformType.TO_STRING: TransformFunctions.to_string,
    }
    
    @classmethod
    def apply_transform(
        cls,
        value: Any,
        transform_type: TransformType,
        config: dict | None = None
    ) -> Any:
        """Apply a single transformation to a value."""
        config = config or {}
        
        if transform_type == TransformType.NONE:
            return value
        
        if transform_type in cls.TRANSFORM_FUNCTIONS:
            return cls.TRANSFORM_FUNCTIONS[transform_type](value)
        
        if transform_type == TransformType.CONCAT:
            values = config.get('values', [value])
            separator = config.get('separator', ' ')
            return TransformFunctions.concat(values, separator)
        
        if transform_type == TransformType.SPLIT:
            separator = config.get('separator', ',')
            index = config.get('index', 0)
            return TransformFunctions.split(value, separator, index)
        
        if transform_type == TransformType.REPLACE:
            old = config.get('old', '')
            new = config.get('new', '')
            return TransformFunctions.replace(value, old, new)
        
        if transform_type == TransformType.FORMAT_DATE:
            output_format = config.get('format', '%Y-%m-%d')
            return TransformFunctions.format_date(value, output_format)
        
        if transform_type == TransformType.TO_NUMBER:
            default = config.get('default', 0)
            return TransformFunctions.to_number(value, default)
        
        if transform_type == TransformType.LOOKUP:
            lookup_table = config.get('lookup_table', {})
            default = config.get('default', '')
            return TransformFunctions.lookup(value, lookup_table, default)
        
        if transform_type == TransformType.CUSTOM:
            # Custom transform using safe expression evaluation
            # Only supports basic operations: string operations and type conversions
            expression = config.get('expression', '')
            if expression and value is not None:
                try:
                    # Safe string-based transformations only
                    str_value = str(value)
                    if expression == 'upper':
                        return str_value.upper()
                    elif expression == 'lower':
                        return str_value.lower()
                    elif expression == 'strip':
                        return str_value.strip()
                    elif expression == 'title':
                        return str_value.title()
                    elif expression.startswith('prefix:'):
                        prefix = expression[7:]
                        return prefix + str_value
                    elif expression.startswith('suffix:'):
                        suffix = expression[7:]
                        return str_value + suffix
                    elif expression.startswith('replace:'):
                        # Format: replace:old:new
                        parts = expression[8:].split(':')
                        if len(parts) >= 2:
                            return str_value.replace(parts[0], parts[1])
                    elif expression.startswith('slice:'):
                        # Format: slice:start:end
                        parts = expression[6:].split(':')
                        if len(parts) >= 2:
                            start = int(parts[0]) if parts[0] else None
                            end = int(parts[1]) if parts[1] else None
                            return str_value[start:end]
                    # If no matching expression, return original value
                    logger.warning(f"Unknown custom expression: {expression}")
                    return value
                except Exception as e:
                    logger.warning(f"Custom transform failed: {e}")
                    return value
        
        return value
    
    @classmethod
    def apply_mapping_edge(
        cls,
        source_row: pd.Series,
        edge: dict
    ) -> tuple[Any, list[dict]]:
        """
        Apply a single mapping edge to a source row.
        
        Returns:
            Tuple of (transformed value, list of warnings)
        """
        warnings = []
        mapping_type = MappingType(edge.get('mapping_type', 'direct'))
        transform_type = TransformType(edge.get('transform_type', 'none'))
        config = edge.get('transform_config', {}) or {}
        
        if mapping_type == MappingType.CONSTANT:
            return edge.get('constant_value', ''), warnings
        
        source_field = edge.get('source_field_name')
        
        if mapping_type == MappingType.DIRECT:
            if source_field and source_field in source_row.index:
                value = source_row[source_field]
                return cls.apply_transform(value, transform_type, config), warnings
            else:
                warnings.append({
                    'type': 'missing_source',
                    'message': f"Source field '{source_field}' not found"
                })
                return None, warnings
        
        if mapping_type == MappingType.TRANSFORM:
            if source_field and source_field in source_row.index:
                value = source_row[source_field]
                return cls.apply_transform(value, transform_type, config), warnings
            else:
                warnings.append({
                    'type': 'missing_source',
                    'message': f"Source field '{source_field}' not found"
                })
                return None, warnings
        
        if mapping_type == MappingType.CONCAT:
            # Get additional source fields for concatenation
            additional_fields = edge.get('additional_source_fields', [])
            all_fields = [source_field] + additional_fields if source_field else additional_fields
            
            values = []
            for field in all_fields:
                if field in source_row.index:
                    values.append(source_row[field])
                else:
                    warnings.append({
                        'type': 'missing_source',
                        'message': f"Source field '{field}' not found for concat"
                    })
            
            separator = config.get('separator', ' ')
            return TransformFunctions.concat(values, separator), warnings
        
        if mapping_type == MappingType.SPLIT:
            if source_field and source_field in source_row.index:
                value = source_row[source_field]
                separator = config.get('separator', ',')
                index = config.get('index', 0)
                return TransformFunctions.split(value, separator, index), warnings
            else:
                return None, warnings
        
        if mapping_type == MappingType.LOOKUP:
            if source_field and source_field in source_row.index:
                value = source_row[source_field]
                lookup_table = edge.get('lookup_table', {}) or config.get('lookup_table', {})
                default = config.get('default', '')
                result = TransformFunctions.lookup(value, lookup_table, default)
                if result == default and default == '':
                    warnings.append({
                        'type': 'lookup_not_found',
                        'message': f"No lookup match for value '{value}'"
                    })
                return result, warnings
            else:
                return None, warnings
        
        return None, warnings
    
    @classmethod
    def apply_mappings(
        cls,
        source_df: pd.DataFrame,
        edges: list[dict],
        target_fields: list[str]
    ) -> tuple[pd.DataFrame, list[dict]]:
        """
        Apply all mapping edges to transform source DataFrame.
        
        Returns:
            Tuple of (transformed DataFrame, list of all warnings)
        """
        all_warnings = []
        result_data = []
        
        # Build edge lookup by target field
        edge_by_target = {e.get('target_field_name'): e for e in edges}
        
        for idx, source_row in source_df.iterrows():
            target_row = {}
            
            for target_field in target_fields:
                edge = edge_by_target.get(target_field)
                
                if edge:
                    value, warnings = cls.apply_mapping_edge(source_row, edge)
                    target_row[target_field] = value
                    
                    for warning in warnings:
                        warning['row_index'] = idx
                        warning['target_field'] = target_field
                        all_warnings.append(warning)
                else:
                    # No mapping defined - leave as None
                    target_row[target_field] = None
            
            result_data.append(target_row)
        
        result_df = pd.DataFrame(result_data)
        return result_df, all_warnings
    
    @classmethod
    def preview_mapping(
        cls,
        source_df: pd.DataFrame,
        edge: dict,
        preview_rows: int = 10
    ) -> list[dict]:
        """
        Preview a single mapping edge on sample data.
        
        Returns:
            List of preview rows with source and target values
        """
        previews = []
        sample_df = source_df.head(preview_rows)
        
        for idx, source_row in sample_df.iterrows():
            value, warnings = cls.apply_mapping_edge(source_row, edge)
            
            source_field = edge.get('source_field_name')
            source_value = source_row.get(source_field) if source_field else None
            
            previews.append({
                'row_index': idx,
                'source_value': source_value,
                'target_value': value,
                'warnings': warnings
            })
        
        return previews
