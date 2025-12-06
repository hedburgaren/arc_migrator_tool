/**
 * API service for file operations
 */
import { FileMetadata, FileUploadResponse } from '../types/file';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Upload a file to the server
 */
export async function uploadFile(file: File): Promise<FileUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    try {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload file');
    } catch (e) {
      throw new Error('Failed to upload file');
    }
  }

  return response.json();
}

/**
 * Get list of all uploaded files
 */
export async function listFiles(): Promise<FileMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/api/files`);

  if (!response.ok) {
    throw new Error('Failed to fetch files');
  }

  return response.json();
}

/**
 * Get metadata for a specific file
 */
export async function getFile(fileId: number): Promise<FileMetadata> {
  const response = await fetch(`${API_BASE_URL}/api/files/${fileId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch file');
  }

  return response.json();
}

/**
 * Delete a file
 */
export async function deleteFile(fileId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/files/${fileId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to delete file');
  }
}

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format date in human-readable format
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleString();
}

/**
 * Trigger schema analysis for a file
 */
export async function analyzeFileSchema(
  fileId: number,
  sampleSize: number = 5
): Promise<{ message: string; file_id: number; row_count: number; column_count: number }> {
  const response = await fetch(`${API_BASE_URL}/api/files/${fileId}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ sample_size: sampleSize }),
  });

  if (!response.ok) {
    try {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to analyze file schema');
    } catch (e) {
      throw new Error('Failed to analyze file schema');
    }
  }

  return response.json();
}

/**
 * Get schema for a file
 */
export async function getFileSchema(fileId: number): Promise<import('../types/schema').FileSchemaResponse> {
  const response = await fetch(`${API_BASE_URL}/api/files/${fileId}/schema`);

  if (!response.ok) {
    try {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch schema');
    } catch (e) {
      throw new Error('Failed to fetch schema');
    }
  }

  return response.json();
}
