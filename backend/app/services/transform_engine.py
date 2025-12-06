"""
Transform engine for applying field mappings and transforming data.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class TransformEngine:
    """Service for executing data transformations based on field mappings."""
    
    def __init__(self):
        """Initialize transform engine."""
        self.transform_handlers = {
            "1:1": self._transform_one_to_one,
            "constant": self._transform_constant,
            "concat": self._transform_concat,
            "split": self._transform_split,
            "custom": self._transform_custom,
        }
    
    def execute_transformations(
        self,
        source_data: pd.DataFrame,
        mappings: List[Dict[str, Any]]
    ) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Apply all mappings to transform source data.
        
        Args:
            source_data: Source DataFrame
            mappings: List of mapping configurations
            
        Returns:
            Tuple of (transformed_dataframe, list_of_errors)
        """
        if source_data.empty:
            return pd.DataFrame(), []
        
        errors = []
        transformed_data = {}
        
        # Process each mapping
        for mapping in mappings:
            try:
                target_field = mapping.get("target_field")
                if not target_field:
                    errors.append({
                        "mapping_id": mapping.get("id"),
                        "error": "Missing target_field in mapping"
                    })
                    continue
                
                # Apply the transformation
                transformed_values, mapping_errors = self.apply_mapping(source_data, mapping)
                
                if mapping_errors:
                    errors.extend(mapping_errors)
                
                if transformed_values is not None:
                    transformed_data[target_field] = transformed_values
                    
            except Exception as e:
                logger.error(f"Error processing mapping {mapping.get('id')}: {str(e)}")
                errors.append({
                    "mapping_id": mapping.get("id"),
                    "source_field": mapping.get("source_field"),
                    "target_field": mapping.get("target_field"),
                    "error": str(e)
                })
        
        # Create result DataFrame
        result_df = pd.DataFrame(transformed_data) if transformed_data else pd.DataFrame()
        
        return result_df, errors
    
    def apply_mapping(
        self,
        data: pd.DataFrame,
        mapping: Dict[str, Any]
    ) -> Tuple[Optional[pd.Series], List[Dict[str, Any]]]:
        """
        Apply a single mapping transformation.
        
        Args:
            data: Source DataFrame
            mapping: Mapping configuration
            
        Returns:
            Tuple of (transformed_series, list_of_errors)
        """
        transform_type = mapping.get("transform_type", "1:1")
        handler = self.transform_handlers.get(transform_type)
        
        if not handler:
            return None, [{
                "mapping_id": mapping.get("id"),
                "error": f"Unknown transform type: {transform_type}"
            }]
        
        try:
            return handler(data, mapping)
        except Exception as e:
            logger.error(f"Transform handler error for {transform_type}: {str(e)}")
            return None, [{
                "mapping_id": mapping.get("id"),
                "transform_type": transform_type,
                "error": str(e)
            }]
    
    def _transform_one_to_one(
        self,
        data: pd.DataFrame,
        mapping: Dict[str, Any]
    ) -> Tuple[pd.Series, List[Dict[str, Any]]]:
        """
        Direct 1:1 field mapping with optional type conversion.
        
        Args:
            data: Source DataFrame
            mapping: Mapping configuration
            
        Returns:
            Tuple of (transformed_series, list_of_errors)
        """
        source_field = mapping.get("source_field")
        errors = []
        
        if source_field not in data.columns:
            return pd.Series([None] * len(data)), [{
                "mapping_id": mapping.get("id"),
                "error": f"Source field '{source_field}' not found in data"
            }]
        
        series = data[source_field].copy()
        
        # Apply type conversion if specified
        transform_config = mapping.get("transform_config") or {}
        target_type = transform_config.get("target_type")
        
        if target_type:
            series, conversion_errors = self._convert_type(series, target_type, mapping)
            errors.extend(conversion_errors)
        
        # Handle null values
        null_handling = transform_config.get("null_handling", "keep")
        if null_handling == "replace":
            default_value = transform_config.get("default_value", "")
            series = series.fillna(default_value)
        elif null_handling == "remove":
            # Mark nulls but don't remove (caller can decide)
            pass
        
        return series, errors
    
    def _transform_constant(
        self,
        data: pd.DataFrame,
        mapping: Dict[str, Any]
    ) -> Tuple[pd.Series, List[Dict[str, Any]]]:
        """
        Set a constant value for all rows.
        
        Args:
            data: Source DataFrame
            mapping: Mapping configuration
            
        Returns:
            Tuple of (transformed_series, list_of_errors)
        """
        transform_config = mapping.get("transform_config") or {}
        constant_value = transform_config.get("constant_value", "")
        
        series = pd.Series([constant_value] * len(data))
        return series, []
    
    def _transform_concat(
        self,
        data: pd.DataFrame,
        mapping: Dict[str, Any]
    ) -> Tuple[pd.Series, List[Dict[str, Any]]]:
        """
        Concatenate multiple source fields.
        
        Args:
            data: Source DataFrame
            mapping: Mapping configuration
            
        Returns:
            Tuple of (transformed_series, list_of_errors)
        """
        transform_config = mapping.get("transform_config") or {}
        source_fields = transform_config.get("source_fields", [])
        separator = transform_config.get("separator", " ")
        errors = []
        
        if not source_fields:
            # Fallback to single source_field
            source_field = mapping.get("source_field")
            if source_field:
                source_fields = [source_field]
        
        if not source_fields:
            return pd.Series([None] * len(data)), [{
                "mapping_id": mapping.get("id"),
                "error": "No source fields specified for concatenation"
            }]
        
        # Collect valid fields
        valid_series = []
        for field in source_fields:
            if field in data.columns:
                valid_series.append(data[field].astype(str).fillna(""))
            else:
                errors.append({
                    "mapping_id": mapping.get("id"),
                    "error": f"Source field '{field}' not found for concatenation"
                })
        
        if not valid_series:
            return pd.Series([None] * len(data)), errors
        
        # Concatenate with separator
        result = valid_series[0]
        for s in valid_series[1:]:
            result = result + separator + s
        
        return result, errors
    
    def _transform_split(
        self,
        data: pd.DataFrame,
        mapping: Dict[str, Any]
    ) -> Tuple[pd.Series, List[Dict[str, Any]]]:
        """
        Split a field and extract a specific part.
        
        Args:
            data: Source DataFrame
            mapping: Mapping configuration
            
        Returns:
            Tuple of (transformed_series, list_of_errors)
        """
        source_field = mapping.get("source_field")
        transform_config = mapping.get("transform_config") or {}
        separator = transform_config.get("separator", " ")
        index = transform_config.get("index", 0)
        errors = []
        
        if source_field not in data.columns:
            return pd.Series([None] * len(data)), [{
                "mapping_id": mapping.get("id"),
                "error": f"Source field '{source_field}' not found"
            }]
        
        try:
            result = data[source_field].astype(str).str.split(separator).str[index]
            return result, errors
        except Exception as e:
            return pd.Series([None] * len(data)), [{
                "mapping_id": mapping.get("id"),
                "error": f"Split operation failed: {str(e)}"
            }]
    
    def _transform_custom(
        self,
        data: pd.DataFrame,
        mapping: Dict[str, Any]
    ) -> Tuple[pd.Series, List[Dict[str, Any]]]:
        """
        Custom transformation (placeholder for extensibility).
        
        Args:
            data: Source DataFrame
            mapping: Mapping configuration
            
        Returns:
            Tuple of (transformed_series, list_of_errors)
        """
        # For now, fallback to 1:1
        return self._transform_one_to_one(data, mapping)
    
    def _convert_type(
        self,
        series: pd.Series,
        target_type: str,
        mapping: Dict[str, Any]
    ) -> Tuple[pd.Series, List[Dict[str, Any]]]:
        """
        Convert series to target data type.
        
        Args:
            series: Input series
            target_type: Target data type (string, integer, float, date, boolean)
            mapping: Mapping configuration for error reporting
            
        Returns:
            Tuple of (converted_series, list_of_errors)
        """
        errors = []
        
        try:
            if target_type == "string":
                return series.astype(str), errors
            
            elif target_type == "integer":
                # Convert to numeric, then to int (coerce errors to NaN)
                converted = pd.to_numeric(series, errors='coerce')
                return converted.astype('Int64'), errors
            
            elif target_type == "float":
                return pd.to_numeric(series, errors='coerce'), errors
            
            elif target_type == "date":
                converted = pd.to_datetime(series, errors='coerce')
                return converted, errors
            
            elif target_type == "boolean":
                # Handle various boolean representations
                if series.dtype == 'bool':
                    return series, errors
                
                # Convert common string representations
                bool_map = {
                    'true': True, 'false': False,
                    'yes': True, 'no': False,
                    '1': True, '0': False,
                    't': True, 'f': False,
                    'y': True, 'n': False
                }
                
                return series.astype(str).str.lower().map(bool_map).fillna(False), errors
            
            else:
                errors.append({
                    "mapping_id": mapping.get("id"),
                    "error": f"Unknown target type: {target_type}"
                })
                return series, errors
                
        except Exception as e:
            errors.append({
                "mapping_id": mapping.get("id"),
                "error": f"Type conversion to {target_type} failed: {str(e)}"
            })
            return series, errors
    
    def validate_transform(
        self,
        mapping: Dict[str, Any],
        sample_data: pd.DataFrame
    ) -> Tuple[bool, List[str]]:
        """
        Validate a mapping configuration against sample data.
        
        Args:
            mapping: Mapping configuration
            sample_data: Sample DataFrame for validation
            
        Returns:
            Tuple of (is_valid, list_of_validation_errors)
        """
        validation_errors = []
        
        # Check required fields
        if not mapping.get("target_field"):
            validation_errors.append("Missing target_field")
        
        transform_type = mapping.get("transform_type", "1:1")
        if transform_type not in self.transform_handlers:
            validation_errors.append(f"Unknown transform_type: {transform_type}")
        
        # Validate based on transform type
        if transform_type in ["1:1", "split"]:
            source_field = mapping.get("source_field")
            if not source_field:
                validation_errors.append("Missing source_field")
            elif source_field not in sample_data.columns:
                validation_errors.append(f"Source field '{source_field}' not found in data")
        
        elif transform_type == "concat":
            transform_config = mapping.get("transform_config") or {}
            source_fields = transform_config.get("source_fields", [])
            if not source_fields:
                validation_errors.append("Missing source_fields for concatenation")
            else:
                for field in source_fields:
                    if field not in sample_data.columns:
                        validation_errors.append(f"Source field '{field}' not found for concatenation")
        
        elif transform_type == "constant":
            transform_config = mapping.get("transform_config") or {}
            if "constant_value" not in transform_config:
                validation_errors.append("Missing constant_value")
        
        return len(validation_errors) == 0, validation_errors
