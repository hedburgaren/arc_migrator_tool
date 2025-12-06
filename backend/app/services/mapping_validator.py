"""
Mapping validation service for validating field mappings.
"""
import logging
from typing import List, Dict, Any, Set, Tuple, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class MappingValidator:
    """Service for validating field mappings."""
    
    def __init__(self):
        """Initialize mapping validator."""
        pass
    
    def validate_mappings(
        self,
        mappings: List[Dict[str, Any]],
        source_schema: List[str],
        target_schema: Optional[List[str]] = None,
        check_completeness: bool = True,
        check_type_compatibility: bool = True,
        check_circular_deps: bool = True,
        required_fields: Optional[List[str]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Validate field mappings.
        
        Args:
            mappings: List of mapping configurations
            source_schema: List of source field names
            target_schema: Optional list of target field names
            check_completeness: Whether to check completeness
            check_type_compatibility: Whether to check type compatibility
            check_circular_deps: Whether to check circular dependencies
            required_fields: List of required target fields
            
        Returns:
            Tuple of (status, list_of_issues)
            Status is one of: 'passed', 'warning', 'failed'
        """
        issues = []
        
        # Check for empty mappings
        if not mappings:
            issues.append({
                'severity': 'warning',
                'message': 'No mappings defined',
                'field': None,
                'details': {}
            })
            return 'warning', issues
        
        # Check each mapping
        for mapping in mappings:
            mapping_issues = self._validate_single_mapping(mapping, source_schema)
            issues.extend(mapping_issues)
        
        # Check for duplicate target fields
        duplicate_issues = self._check_duplicate_targets(mappings)
        issues.extend(duplicate_issues)
        
        # Check circular dependencies
        if check_circular_deps:
            circular_issues = self._check_circular_dependencies(mappings)
            issues.extend(circular_issues)
        
        # Check required fields
        if check_completeness and required_fields:
            required_issues = self._check_required_fields(mappings, required_fields)
            issues.extend(required_issues)
        
        # Determine overall status
        has_errors = any(issue['severity'] == 'error' for issue in issues)
        has_warnings = any(issue['severity'] == 'warning' for issue in issues)
        
        if has_errors:
            return 'failed', issues
        elif has_warnings:
            return 'warning', issues
        else:
            return 'passed', issues
    
    def _validate_single_mapping(
        self,
        mapping: Dict[str, Any],
        source_schema: List[str]
    ) -> List[Dict[str, Any]]:
        """Validate a single mapping."""
        issues = []
        
        # Check required fields
        if not mapping.get('target_field'):
            issues.append({
                'severity': 'error',
                'message': 'Missing target_field',
                'field': None,
                'details': {'mapping_id': mapping.get('id')}
            })
        
        transform_type = mapping.get('transform_type', '1:1')
        
        # Validate based on transform type
        if transform_type in ['1:1', 'split']:
            source_field = mapping.get('source_field')
            if not source_field:
                issues.append({
                    'severity': 'error',
                    'message': f'Missing source_field for {transform_type} mapping',
                    'field': mapping.get('target_field'),
                    'details': {'mapping_id': mapping.get('id')}
                })
            elif source_field not in source_schema:
                issues.append({
                    'severity': 'error',
                    'message': f"Source field '{source_field}' not found in source schema",
                    'field': mapping.get('target_field'),
                    'details': {'mapping_id': mapping.get('id'), 'source_field': source_field}
                })
        
        elif transform_type == 'concat':
            transform_config = mapping.get('transform_config') or {}
            source_fields = transform_config.get('source_fields', [])
            
            if not source_fields:
                issues.append({
                    'severity': 'error',
                    'message': 'Missing source_fields for concatenation',
                    'field': mapping.get('target_field'),
                    'details': {'mapping_id': mapping.get('id')}
                })
            else:
                for field in source_fields:
                    if field not in source_schema:
                        issues.append({
                            'severity': 'error',
                            'message': f"Source field '{field}' not found for concatenation",
                            'field': mapping.get('target_field'),
                            'details': {'mapping_id': mapping.get('id'), 'source_field': field}
                        })
        
        elif transform_type == 'constant':
            transform_config = mapping.get('transform_config') or {}
            if 'constant_value' not in transform_config:
                issues.append({
                    'severity': 'warning',
                    'message': 'Missing constant_value for constant mapping',
                    'field': mapping.get('target_field'),
                    'details': {'mapping_id': mapping.get('id')}
                })
        
        return issues
    
    def _check_duplicate_targets(
        self,
        mappings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for duplicate target fields."""
        issues = []
        
        target_fields = {}
        for mapping in mappings:
            target_field = mapping.get('target_field')
            if target_field:
                if target_field in target_fields:
                    issues.append({
                        'severity': 'error',
                        'message': f"Duplicate target field: '{target_field}'",
                        'field': target_field,
                        'details': {
                            'mapping_ids': [target_fields[target_field], mapping.get('id')]
                        }
                    })
                else:
                    target_fields[target_field] = mapping.get('id')
        
        return issues
    
    def _check_circular_dependencies(
        self,
        mappings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for circular dependencies in mappings."""
        issues = []
        
        # Build dependency graph
        dependencies = {}
        for mapping in mappings:
            target = mapping.get('target_field')
            if not target:
                continue
            
            sources = []
            transform_type = mapping.get('transform_type', '1:1')
            
            if transform_type in ['1:1', 'split']:
                source = mapping.get('source_field')
                if source:
                    sources.append(source)
            elif transform_type == 'concat':
                config = mapping.get('transform_config') or {}
                sources = config.get('source_fields', [])
            
            dependencies[target] = sources
        
        # Check for circular dependencies using DFS
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor in dependencies:  # Only check if neighbor is also a target
                    if neighbor not in visited:
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in dependencies:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    issues.append({
                        'severity': 'error',
                        'message': f"Circular dependency detected involving field '{node}'",
                        'field': node,
                        'details': {}
                    })
        
        return issues
    
    def _check_required_fields(
        self,
        mappings: List[Dict[str, Any]],
        required_fields: List[str]
    ) -> List[Dict[str, Any]]:
        """Check if all required fields are mapped."""
        issues = []
        
        mapped_fields = {m.get('target_field') for m in mappings if m.get('target_field')}
        
        for field in required_fields:
            if field not in mapped_fields:
                issues.append({
                    'severity': 'warning',
                    'message': f"Required field '{field}' is not mapped",
                    'field': field,
                    'details': {}
                })
        
        return issues
