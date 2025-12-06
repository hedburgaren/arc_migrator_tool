/**
 * File upload component with drag-and-drop support
 */
import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { uploadFile } from '../services/api';
import { UploadStatus } from '../types/file';
import './FileUpload.css';

interface FileUploadProps {
  onUploadSuccess: () => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [error, setError] = useState<string>('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    // Validate file type
    const allowedExtensions = ['.csv', '.xlsx', '.xls'];
    const lastDotIndex = file.name.lastIndexOf('.');
    
    if (lastDotIndex === -1) {
      setError('File must have an extension');
      setStatus('error');
      return;
    }
    
    const fileExt = file.name.substring(lastDotIndex).toLowerCase();
    
    if (!allowedExtensions.includes(fileExt)) {
      setError(`Invalid file type. Allowed types: ${allowedExtensions.join(', ')}`);
      setStatus('error');
      return;
    }

    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File too large. Maximum size: 100MB');
      setStatus('error');
      return;
    }

    setStatus('uploading');
    setError('');

    try {
      await uploadFile(file);
      setStatus('success');
      onUploadSuccess();
      
      // Reset status after 3 seconds
      setTimeout(() => {
        setStatus('idle');
      }, 3000);
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload-container">
      <div
        className={`file-upload-dropzone ${isDragging ? 'dragging' : ''} ${status}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        {status === 'idle' && (
          <>
            <div className="upload-icon">📁</div>
            <p className="upload-text">
              <strong>Click to upload</strong> or drag and drop
            </p>
            <p className="upload-hint">CSV or Excel files (max 100MB)</p>
          </>
        )}

        {status === 'uploading' && (
          <>
            <div className="upload-spinner">⏳</div>
            <p className="upload-text">Uploading...</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="upload-icon success">✓</div>
            <p className="upload-text success">File uploaded successfully!</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="upload-icon error">✕</div>
            <p className="upload-text error">Upload failed</p>
            {error && <p className="error-message">{error}</p>}
          </>
        )}
      </div>
    </div>
  );
}
