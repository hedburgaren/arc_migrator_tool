/**
 * Type definitions for file operations
 */

export interface FileMetadata {
  id: number;
  filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  upload_timestamp: string;
  status: string;
  schema_analyzed: boolean;
  column_count: number | null;
  row_count: number | null;
  encoding: string | null;
}

export interface FileUploadResponse {
  id: number;
  filename: string;
  file_size: number;
  file_type: string;
  upload_timestamp: string;
  message: string;
}

export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';
