/**
 * Custom node component for displaying schema fields
 */
import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { SchemaFieldNode } from '../types/mapping';
import './SchemaNode.css';

function SchemaNode({ data }: NodeProps<SchemaFieldNode>) {
  const isSource = data.side === 'source';
  
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

  const formatSampleValues = (values: any[] | undefined): string => {
    if (!values || values.length === 0) return '';
    const formatted = values.slice(0, 2).map(v => {
      if (v === null || v === undefined) return 'null';
      if (typeof v === 'string') return v.length > 20 ? `${v.substring(0, 20)}...` : v;
      return String(v);
    }).join(', ');
    return values.length > 2 ? `${formatted}...` : formatted;
  };

  return (
    <div className={`schema-node ${data.side}-node`}>
      {isSource && (
        <Handle
          type="source"
          position={Position.Right}
          className="schema-handle source-handle"
          id={`${data.id}-source`}
        />
      )}
      {!isSource && (
        <Handle
          type="target"
          position={Position.Left}
          className="schema-handle target-handle"
          id={`${data.id}-target`}
        />
      )}
      
      <div className="schema-node-content">
        <div className="schema-node-header">
          <span className="field-icon">{getDataTypeIcon(data.dataType)}</span>
          <span className="field-name">{data.fieldName}</span>
        </div>
        <div className="schema-node-meta">
          <span className="field-type">{data.dataType}</span>
          {data.uniqueCount !== undefined && (
            <span className="field-stat">
              {data.uniqueCount} unique
            </span>
          )}
        </div>
        {data.sampleValues && data.sampleValues.length > 0 && (
          <div className="schema-node-samples">
            {formatSampleValues(data.sampleValues)}
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(SchemaNode);
