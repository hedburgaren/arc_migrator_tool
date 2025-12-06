/**
 * Type definitions for schema operations
 */

export interface ColumnSchema {
  id: number;
  column_name: string;
  column_index: number;
  data_type: string;
  sample_values: any[] | null;
  null_count: number;
  unique_count: number;
  statistics: ColumnStatistics | null;
}

export interface ColumnStatistics {
  min: number;
  max: number;
  mean: number;
  median: number;
  std: number;
}

export interface FileSchemaResponse {
  file_id: number;
  filename: string;
  row_count: number;
  column_count: number;
  encoding: string | null;
  columns: ColumnSchema[];
}

export interface SchemaAnalysisRequest {
  sample_size?: number;
}
