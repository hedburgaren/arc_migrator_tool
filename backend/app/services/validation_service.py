"""Validation service for data validation."""

import logging
import re
from typing import Any

import pandas as pd
from dateutil import parser as date_parser

from app.models.schema import FieldType

logger = logging.getLogger(__name__)


class ValidationError:
    """Validation error container."""
    
    def __init__(
        self,
        field_name: str,
        row_index: int | None,
        message: str,
        value: Any = None,
        rule: str | None = None
    ):
        self.field_name = field_name
        self.row_index = row_index
        self.message = message
        self.value = value
        self.rule = rule
    
    def to_dict(self) -> dict:
        return {
            'field_name': self.field_name,
            'row_index': self.row_index,
            'message': self.message,
            'value': self.value,
            'rule': self.rule
        }


class ValidationService:
    """Service for validating data against rules."""
    
    @classmethod
    def validate_required(cls, value: Any) -> bool:
        """Check if value is not empty."""
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if pd.isna(value):
            return False
        return True
    
    @classmethod
    def validate_type(cls, value: Any, field_type: FieldType) -> bool:
        """Check if value matches expected type."""
        if value is None or pd.isna(value):
            return True  # Null values handled by required validation
        
        if field_type == FieldType.STRING:
            return True
        
        if field_type == FieldType.INTEGER:
            try:
                int(float(value))
                return True
            except (ValueError, TypeError):
                return False
        
        if field_type == FieldType.FLOAT:
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        
        if field_type == FieldType.BOOLEAN:
            bool_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
            return str(value).lower().strip() in bool_values
        
        if field_type in {FieldType.DATE, FieldType.DATETIME}:
            try:
                date_parser.parse(str(value))
                return True
            except (ValueError, TypeError):
                return False
        
        return True
    
    @classmethod
    def validate_pattern(cls, value: Any, pattern: str) -> bool:
        """Check if value matches regex pattern."""
        if value is None or pd.isna(value):
            return True
        return bool(re.match(pattern, str(value)))
    
    @classmethod
    def validate_min_length(cls, value: Any, min_length: int) -> bool:
        """Check if value meets minimum length."""
        if value is None or pd.isna(value):
            return True
        return len(str(value)) >= min_length
    
    @classmethod
    def validate_max_length(cls, value: Any, max_length: int) -> bool:
        """Check if value meets maximum length."""
        if value is None or pd.isna(value):
            return True
        return len(str(value)) <= max_length
    
    @classmethod
    def validate_min_value(cls, value: Any, min_value: float) -> bool:
        """Check if numeric value meets minimum."""
        if value is None or pd.isna(value):
            return True
        try:
            return float(value) >= min_value
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_max_value(cls, value: Any, max_value: float) -> bool:
        """Check if numeric value meets maximum."""
        if value is None or pd.isna(value):
            return True
        try:
            return float(value) <= max_value
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_enum(cls, value: Any, allowed_values: list) -> bool:
        """Check if value is in allowed list."""
        if value is None or pd.isna(value):
            return True
        return str(value) in [str(v) for v in allowed_values]
    
    @classmethod
    def validate_field(
        cls,
        value: Any,
        field_def: dict,
        rules: dict | None = None
    ) -> list[ValidationError]:
        """
        Validate a single field value against its definition and rules.
        
        Args:
            value: The value to validate
            field_def: Field definition dict
            rules: Additional validation rules
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        field_name = field_def.get('name', 'unknown')
        
        # Check required
        if field_def.get('is_required', False) and not cls.validate_required(value):
            errors.append(ValidationError(
                field_name=field_name,
                row_index=None,
                message=f"Field '{field_name}' is required",
                value=value,
                rule='required'
            ))
            return errors  # No point checking other rules if required failed
        
        # Skip other validations if value is empty
        if not cls.validate_required(value):
            return errors
        
        # Check type
        field_type = field_def.get('field_type')
        if field_type:
            if isinstance(field_type, str):
                field_type = FieldType(field_type)
            if not cls.validate_type(value, field_type):
                errors.append(ValidationError(
                    field_name=field_name,
                    row_index=None,
                    message=f"Invalid type for field '{field_name}': expected {field_type.value}",
                    value=value,
                    rule='type'
                ))
        
        # Apply additional rules
        if rules:
            validation_rules = rules.get(field_name, {})
            
            if 'pattern' in validation_rules:
                if not cls.validate_pattern(value, validation_rules['pattern']):
                    errors.append(ValidationError(
                        field_name=field_name,
                        row_index=None,
                        message=f"Field '{field_name}' does not match pattern",
                        value=value,
                        rule='pattern'
                    ))
            
            if 'min_length' in validation_rules:
                if not cls.validate_min_length(value, validation_rules['min_length']):
                    errors.append(ValidationError(
                        field_name=field_name,
                        row_index=None,
                        message=f"Field '{field_name}' is too short",
                        value=value,
                        rule='min_length'
                    ))
            
            if 'max_length' in validation_rules:
                if not cls.validate_max_length(value, validation_rules['max_length']):
                    errors.append(ValidationError(
                        field_name=field_name,
                        row_index=None,
                        message=f"Field '{field_name}' is too long",
                        value=value,
                        rule='max_length'
                    ))
            
            if 'min_value' in validation_rules:
                if not cls.validate_min_value(value, validation_rules['min_value']):
                    errors.append(ValidationError(
                        field_name=field_name,
                        row_index=None,
                        message=f"Field '{field_name}' is below minimum",
                        value=value,
                        rule='min_value'
                    ))
            
            if 'max_value' in validation_rules:
                if not cls.validate_max_value(value, validation_rules['max_value']):
                    errors.append(ValidationError(
                        field_name=field_name,
                        row_index=None,
                        message=f"Field '{field_name}' exceeds maximum",
                        value=value,
                        rule='max_value'
                    ))
            
            if 'allowed_values' in validation_rules:
                if not cls.validate_enum(value, validation_rules['allowed_values']):
                    errors.append(ValidationError(
                        field_name=field_name,
                        row_index=None,
                        message=f"Field '{field_name}' has invalid value",
                        value=value,
                        rule='allowed_values'
                    ))
        
        return errors
    
    @classmethod
    def validate_row(
        cls,
        row: pd.Series,
        field_defs: list[dict],
        rules: dict | None = None,
        row_index: int | None = None
    ) -> list[dict]:
        """Validate a single row against field definitions."""
        errors = []
        
        for field_def in field_defs:
            field_name = field_def.get('name', '')
            value = row.get(field_name)
            
            field_errors = cls.validate_field(value, field_def, rules)
            for error in field_errors:
                error.row_index = row_index
                errors.append(error.to_dict())
        
        return errors
    
    @classmethod
    def validate_dataframe(
        cls,
        df: pd.DataFrame,
        field_defs: list[dict],
        rules: dict | None = None,
        max_errors: int = 1000
    ) -> list[dict]:
        """
        Validate entire DataFrame against field definitions.
        
        Args:
            df: DataFrame to validate
            field_defs: List of field definitions
            rules: Additional validation rules
            max_errors: Maximum errors to return
            
        Returns:
            List of validation error dicts
        """
        all_errors = []
        
        for idx, row in df.iterrows():
            if len(all_errors) >= max_errors:
                all_errors.append({
                    'message': f"Maximum errors reached ({max_errors}). Additional errors suppressed.",
                    'row_index': None,
                    'field_name': None
                })
                break
            
            row_errors = cls.validate_row(row, field_defs, rules, row_index=idx)
            all_errors.extend(row_errors)
        
        return all_errors
    
    @classmethod
    def get_validation_summary(cls, errors: list[dict]) -> dict:
        """Get summary of validation errors."""
        summary = {
            'total_errors': len(errors),
            'errors_by_field': {},
            'errors_by_rule': {},
            'affected_rows': set()
        }
        
        for error in errors:
            field = error.get('field_name', 'unknown')
            rule = error.get('rule', 'unknown')
            row = error.get('row_index')
            
            summary['errors_by_field'][field] = summary['errors_by_field'].get(field, 0) + 1
            summary['errors_by_rule'][rule] = summary['errors_by_rule'].get(rule, 0) + 1
            if row is not None:
                summary['affected_rows'].add(row)
        
        summary['affected_rows'] = len(summary['affected_rows'])
        return summary
