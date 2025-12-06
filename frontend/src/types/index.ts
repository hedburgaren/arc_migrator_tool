// Project types
export interface Project {
  id: number
  name: string
  description: string | null
  source_system: string
  target_system: string
  status: ProjectStatus
  created_at: string
  updated_at: string
}

export type ProjectStatus = 'draft' | 'mapping' | 'ready' | 'executing' | 'completed' | 'failed'

export interface ProjectCreate {
  name: string
  description?: string
  source_system: string
  target_system: string
}

// File types
export interface SourceFile {
  id: number
  project_id: number
  filename: string
  original_filename: string
  file_type: string
  file_size: number
  encoding: string | null
  row_count: number | null
  column_count: number | null
  sheet_name: string | null
  uploaded_at: string
}

export interface FilePreview {
  file: SourceFile
  columns: string[]
  preview_data: Record<string, unknown>[]
  total_rows: number
}

// Schema types
export interface SchemaDefinition {
  id: number
  project_id: number
  file_id: number | null
  name: string
  schema_type: 'source' | 'target'
  system_type: string
  description: string | null
  created_at: string
}

export interface FieldDefinition {
  id: number
  schema_id: number
  name: string
  display_name: string | null
  field_type: FieldType
  is_required: boolean
  is_primary_key: boolean
  is_lookup: boolean
  unique_values_count: number | null
  sample_values: string[] | null
  position: number
}

export type FieldType = 'string' | 'integer' | 'float' | 'boolean' | 'date' | 'datetime' | 'enum' | 'lookup' | 'json' | 'unknown'

export interface SchemaWithFields extends SchemaDefinition {
  fields: FieldDefinition[]
}

// Mapping types
export interface MappingProfile {
  id: number
  project_id: number
  name: string
  description: string | null
  source_schema_id: number | null
  target_schema_id: number | null
  version: number
  is_active: boolean
  layout_json: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface MappingEdge {
  id: number
  profile_id: number
  source_field_id: number | null
  target_field_id: number
  mapping_type: MappingType
  transform_type: TransformType
  transform_config: Record<string, unknown> | null
  constant_value: string | null
  lookup_table: Record<string, string> | null
  additional_source_fields: number[] | null
  position_x: number | null
  position_y: number | null
}

export type MappingType = 'direct' | 'transform' | 'concat' | 'split' | 'lookup' | 'constant'
export type TransformType = 'none' | 'lowercase' | 'uppercase' | 'trim' | 'concat' | 'split' | 'replace' | 'format_date' | 'to_number' | 'to_string' | 'lookup' | 'custom'

export interface MappingProfileWithEdges extends MappingProfile {
  edges: MappingEdge[]
}

export interface MappingEdgeCreate {
  source_field_id: number | null
  target_field_id: number
  mapping_type: MappingType
  transform_type: TransformType
  transform_config?: Record<string, unknown>
  constant_value?: string
  lookup_table?: Record<string, string>
  additional_source_fields?: number[]
  position_x?: number
  position_y?: number
}

// Execution types
export interface ExecutionRun {
  id: number
  project_id: number
  mapping_profile_id: number
  mode: ExecutionMode
  status: ExecutionStatus
  total_records: number | null
  processed_records: number
  successful_records: number
  failed_records: number
  warnings_count: number
  error_message: string | null
  output_files: string[] | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export type ExecutionMode = 'preview' | 'dry_run' | 'commit'
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface ExecutionLog {
  id: number
  execution_id: number
  level: 'debug' | 'info' | 'warning' | 'error'
  message: string
  record_index: number | null
  field_name: string | null
  source_value: string | null
  target_value: string | null
  timestamp: string
}

export interface ExecutionWithLogs extends ExecutionRun {
  logs: ExecutionLog[]
}

// API response types
export interface ProjectListResponse {
  projects: Project[]
  total: number
}

export interface MappingPreviewResponse {
  profile_id: number
  source_rows: number
  source_data: Record<string, unknown>[]
  transformed_data: Record<string, unknown>[]
  warnings: Array<{
    type: string
    message: string
    row_index?: number
    target_field?: string
  }>
  warnings_count: number
}
