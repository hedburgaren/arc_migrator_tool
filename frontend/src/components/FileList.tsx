/**
 * File list component to display uploaded files
 */
import { useState } from 'react';
import { FileMetadata } from '../types/file';
import { deleteFile, formatFileSize, formatDate } from '../services/api';
import SchemaViewer from './SchemaViewer';
import './FileList.css';

interface FileListProps {
  files: FileMetadata[];
  onFileDeleted: () => void;
}

export default function FileList({ files, onFileDeleted }: FileListProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState<string>('');
  const [selectedFileId, setSelectedFileId] = useState<number | null>(null);

  const handleDelete = async (fileId: number) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return;
    }

    setDeletingId(fileId);
    setError('');

    try {
      await deleteFile(fileId);
      onFileDeleted();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
    } finally {
      setDeletingId(null);
    }
  };

  const selectedFile = files.find(f => f.id === selectedFileId);

  if (files.length === 0) {
    return (
      <div className="file-list-empty">
        <p>No files uploaded yet. Upload a CSV or Excel file to get started.</p>
      </div>
    );
  }

  return (
    <div className="file-list-container">
      <h2 className="file-list-title">Uploaded Files</h2>
      
      {error && (
        <div className="file-list-error">
          {error}
        </div>
      )}

      <div className="file-list">
        {files.map((file) => (
          <div key={file.id} className="file-item">
            <div className="file-info">
              <div className="file-icon">
                {file.filename.endsWith('.csv') ? '📊' : '📈'}
              </div>
              <div className="file-details">
                <h3 className="file-name">{file.filename}</h3>
                <div className="file-meta">
                  <span className="file-size">{formatFileSize(file.file_size)}</span>
                  <span className="file-separator">•</span>
                  <span className="file-date">{formatDate(file.upload_timestamp)}</span>
                  <span className="file-separator">•</span>
                  <span className={`file-status status-${file.status}`}>
                    {file.status}
                  </span>
                  {file.schema_analyzed && file.row_count !== null && file.column_count !== null && (
                    <>
                      <span className="file-separator">•</span>
                      <span className="file-schema-info">
                        {file.row_count.toLocaleString()} rows, {file.column_count} cols
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="file-actions">
              <button
                className="file-schema-btn"
                onClick={() => setSelectedFileId(file.id)}
                title="View schema"
              >
                📋 Schema
              </button>
              <button
                className="file-delete-btn"
                onClick={() => handleDelete(file.id)}
                disabled={deletingId === file.id}
                title="Delete file"
              >
                {deletingId === file.id ? '...' : '🗑️'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedFile && (
        <SchemaViewer
          fileId={selectedFile.id}
          filename={selectedFile.filename}
          schemaAnalyzed={selectedFile.schema_analyzed}
          onClose={() => setSelectedFileId(null)}
        />
      )}
    </div>
  );
}
