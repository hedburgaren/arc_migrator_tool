/**
 * Schema viewer component to display file schema
 */
import { useState, useEffect } from 'react';
import { FileSchemaResponse, ColumnSchema } from '../types/schema';
import { getFileSchema, analyzeFileSchema } from '../services/api';
import './SchemaViewer.css';

interface SchemaViewerProps {
  fileId: number;
  filename: string;
  schemaAnalyzed: boolean;
  onClose: () => void;
}

export default function SchemaViewer({ fileId, filename, schemaAnalyzed, onClose }: SchemaViewerProps) {
  const [schema, setSchema] = useState<FileSchemaResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (schemaAnalyzed) {
      loadSchema();
    }
  }, [fileId, schemaAnalyzed]);

  const loadSchema = async () => {
    try {
      setLoading(true);
      setError('');
      const schemaData = await getFileSchema(fileId);
      setSchema(schemaData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schema');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      setError('');
      await analyzeFileSchema(fileId);
      await loadSchema();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze schema');
    } finally {
      setAnalyzing(false);
    }
  };

  const formatSampleValues = (values: any[] | null): string => {
    if (!values || values.length === 0) return 'N/A';
    return values.map(v => {
      if (v === null || v === undefined) return 'null';
      if (typeof v === 'string') return `"${v}"`;
      return String(v);
    }).join(', ');
  };

  const getDataTypeIcon = (dataType: string): string => {
    switch (dataType) {
      case 'integer':
      case 'float':
        return '🔢';
      case 'string':
        return '📝';
      case 'date':
        return '📅';
      case 'boolean':
        return '✓';
      default:
        return '❓';
    }
  };

  return (
    <div className="schema-viewer-overlay">
      <div className="schema-viewer-modal">
        <div className="schema-viewer-header">
          <h2>Schema: {filename}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="schema-viewer-content">
          {!schemaAnalyzed && !schema && (
            <div className="schema-not-analyzed">
              <p>Schema has not been analyzed yet.</p>
              <button 
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={analyzing}
              >
                {analyzing ? 'Analyzing...' : 'Analyze Schema'}
              </button>
            </div>
          )}

          {error && (
            <div className="schema-error">
              {error}
              {!schemaAnalyzed && (
                <button 
                  className="retry-button"
                  onClick={handleAnalyze}
                  disabled={analyzing}
                >
                  Retry
                </button>
              )}
            </div>
          )}

          {loading && (
            <div className="schema-loading">
              <div className="spinner">⏳</div>
              <p>Loading schema...</p>
            </div>
          )}

          {schema && !loading && (
            <>
              <div className="schema-summary">
                <div className="summary-item">
                  <span className="summary-label">Rows:</span>
                  <span className="summary-value">{schema.row_count.toLocaleString()}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Columns:</span>
                  <span className="summary-value">{schema.column_count}</span>
                </div>
                {schema.encoding && schema.encoding !== 'n/a' && (
                  <div className="summary-item">
                    <span className="summary-label">Encoding:</span>
                    <span className="summary-value">{schema.encoding}</span>
                  </div>
                )}
              </div>

              <div className="schema-table-container">
                <table className="schema-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Column Name</th>
                      <th>Data Type</th>
                      <th>Sample Values</th>
                      <th>Null Count</th>
                      <th>Unique Count</th>
                      <th>Statistics</th>
                    </tr>
                  </thead>
                  <tbody>
                    {schema.columns.map((column: ColumnSchema) => (
                      <tr key={column.id}>
                        <td className="col-index">{column.column_index + 1}</td>
                        <td className="col-name">{column.column_name}</td>
                        <td className="col-type">
                          <span className="type-icon">{getDataTypeIcon(column.data_type)}</span>
                          {column.data_type}
                        </td>
                        <td className="col-samples">
                          {formatSampleValues(column.sample_values)}
                        </td>
                        <td className="col-stat">{column.null_count}</td>
                        <td className="col-stat">{column.unique_count}</td>
                        <td className="col-stats">
                          {column.statistics ? (
                            <div className="stats-detail">
                              <div>Min: {column.statistics.min.toFixed(2)}</div>
                              <div>Max: {column.statistics.max.toFixed(2)}</div>
                              <div>Mean: {column.statistics.mean.toFixed(2)}</div>
                            </div>
                          ) : (
                            'N/A'
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
