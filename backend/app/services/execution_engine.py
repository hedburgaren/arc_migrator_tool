"""Execution engine for running migrations."""

import logging
import csv
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.config import settings
from app.models.execution import ExecutionMode, ExecutionStatus, LogLevel
from app.services.mapping_engine import MappingEngine
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class ExecutionEngineError(Exception):
    """Exception raised for execution errors."""
    pass


class ExecutionResult:
    """Result of an execution run."""
    
    def __init__(self):
        self.status: ExecutionStatus = ExecutionStatus.PENDING
        self.total_records: int = 0
        self.processed_records: int = 0
        self.successful_records: int = 0
        self.failed_records: int = 0
        self.warnings_count: int = 0
        self.logs: list[dict] = []
        self.output_files: list[str] = []
        self.preview_data: list[dict] = []
        self.validation_errors: list[dict] = []
        self.error_message: str | None = None


class ExecutionEngine:
    """Engine for executing migration runs."""
    
    @classmethod
    async def execute(
        cls,
        source_df: pd.DataFrame,
        edges: list[dict],
        target_fields: list[dict],
        mode: ExecutionMode,
        project_id: int,
        profile_id: int,
        validation_rules: dict | None = None
    ) -> ExecutionResult:
        """
        Execute a migration with the specified mode.
        
        Args:
            source_df: Source data DataFrame
            edges: List of mapping edge configurations
            target_fields: List of target field definitions
            mode: Execution mode (preview, dry_run, commit)
            project_id: Project ID for output files
            profile_id: Mapping profile ID
            validation_rules: Optional validation rules
            
        Returns:
            ExecutionResult with status and details
        """
        result = ExecutionResult()
        result.status = ExecutionStatus.RUNNING
        result.total_records = len(source_df)
        
        try:
            # Extract target field names
            target_field_names = [f.get('name') or f.get('field_name') for f in target_fields]
            
            # Apply mappings
            result.logs.append({
                'level': LogLevel.INFO,
                'message': f"Starting {mode.value} execution for {result.total_records} records",
                'timestamp': datetime.utcnow().isoformat()
            })
            
            transformed_df, warnings = MappingEngine.apply_mappings(
                source_df, edges, target_field_names
            )
            
            # Log warnings
            result.warnings_count = len(warnings)
            for warning in warnings[:100]:  # Limit warnings in logs
                result.logs.append({
                    'level': LogLevel.WARNING,
                    'message': warning.get('message', 'Unknown warning'),
                    'record_index': warning.get('row_index'),
                    'field_name': warning.get('target_field'),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Validate if rules provided
            if validation_rules:
                validation_errors = ValidationService.validate_dataframe(
                    transformed_df, target_fields, validation_rules
                )
                result.validation_errors = validation_errors
                
                for error in validation_errors[:100]:
                    result.logs.append({
                        'level': LogLevel.ERROR,
                        'message': error.get('message', 'Validation error'),
                        'record_index': error.get('row_index'),
                        'field_name': error.get('field_name'),
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            if mode == ExecutionMode.PREVIEW:
                # Just return preview data
                result.preview_data = transformed_df.head(settings.DEFAULT_PREVIEW_ROWS).to_dict(orient='records')
                result.processed_records = min(len(transformed_df), settings.DEFAULT_PREVIEW_ROWS)
                result.successful_records = result.processed_records
                result.status = ExecutionStatus.COMPLETED
                
            elif mode == ExecutionMode.DRY_RUN:
                # Process all but don't save
                result.processed_records = len(transformed_df)
                result.successful_records = len(transformed_df) - len(result.validation_errors)
                result.failed_records = len(result.validation_errors)
                result.preview_data = transformed_df.head(settings.DEFAULT_PREVIEW_ROWS).to_dict(orient='records')
                result.status = ExecutionStatus.COMPLETED
                
            elif mode == ExecutionMode.COMMIT:
                # Save output files
                output_files = await cls._save_output(
                    transformed_df,
                    project_id,
                    profile_id
                )
                result.output_files = output_files
                result.processed_records = len(transformed_df)
                result.successful_records = len(transformed_df) - len(result.validation_errors)
                result.failed_records = len(result.validation_errors)
                result.status = ExecutionStatus.COMPLETED
                
                result.logs.append({
                    'level': LogLevel.INFO,
                    'message': f"Migration completed. Output saved to: {', '.join(output_files)}",
                    'timestamp': datetime.utcnow().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.logs.append({
                'level': LogLevel.ERROR,
                'message': f"Execution failed: {e}",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return result
    
    @classmethod
    async def _save_output(
        cls,
        df: pd.DataFrame,
        project_id: int,
        profile_id: int
    ) -> list[str]:
        """Save transformed data to output files."""
        output_dir = Path(settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        base_name = f"project_{project_id}_profile_{profile_id}_{timestamp}"
        
        output_files = []
        
        # Save CSV
        csv_path = output_dir / f"{base_name}.csv"
        df.to_csv(csv_path, index=False, quoting=csv.QUOTE_ALL)
        output_files.append(str(csv_path))
        
        # Save Excel
        xlsx_path = output_dir / f"{base_name}.xlsx"
        df.to_excel(xlsx_path, index=False, sheet_name='Migration Output')
        output_files.append(str(xlsx_path))
        
        logger.info(f"Output saved: {output_files}")
        return output_files
    
    @classmethod
    def generate_sql_output(
        cls,
        df: pd.DataFrame,
        table_name: str,
        project_id: int,
        profile_id: int
    ) -> str:
        """Generate SQL INSERT statements from transformed data."""
        output_dir = Path(settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        sql_path = output_dir / f"project_{project_id}_profile_{profile_id}_{timestamp}.sql"
        
        columns = df.columns.tolist()
        
        with open(sql_path, 'w') as f:
            f.write(f"-- Generated by ARC Migrator Tool\n")
            f.write(f"-- Timestamp: {timestamp}\n")
            f.write(f"-- Total records: {len(df)}\n\n")
            
            for _, row in df.iterrows():
                values = []
                for col in columns:
                    val = row[col]
                    if pd.isna(val):
                        values.append('NULL')
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        # Escape single quotes
                        escaped = str(val).replace("'", "''")
                        values.append(f"'{escaped}'")
                
                cols_str = ', '.join(columns)
                vals_str = ', '.join(values)
                f.write(f"INSERT INTO {table_name} ({cols_str}) VALUES ({vals_str});\n")
        
        return str(sql_path)
    
    @classmethod
    def create_rollback_bundle(
        cls,
        source_df: pd.DataFrame,
        transformed_df: pd.DataFrame,
        edges: list[dict],
        project_id: int,
        profile_id: int
    ) -> dict:
        """Create a rollback bundle with all migration data."""
        return {
            'project_id': project_id,
            'profile_id': profile_id,
            'timestamp': datetime.utcnow().isoformat(),
            'source_row_count': len(source_df),
            'transformed_row_count': len(transformed_df),
            'mapping_edges': edges,
            'source_columns': source_df.columns.tolist(),
            'transformed_columns': transformed_df.columns.tolist(),
        }
