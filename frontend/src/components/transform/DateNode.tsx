/**
 * Date Transform Node Component
 * Handles date parsing, formatting, and manipulation
 */
import { memo, useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import './TransformNode.css';

interface DateConfig {
  input_format?: string;
  output_format: string;
  operation?: string;
  days?: number;
  months?: number;
}

interface DateNodeData {
  label: string;
  config?: DateConfig;
  onConfigChange?: (config: DateConfig) => void;
}

function DateNode({ data, selected }: NodeProps<DateNodeData>) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [inputFormat, setInputFormat] = useState(data.config?.input_format || '');
  const [outputFormat, setOutputFormat] = useState(data.config?.output_format || '%Y-%m-%d');
  const [operation, setOperation] = useState(data.config?.operation || 'format');
  const [days, setDays] = useState(data.config?.days || 0);
  const [months, setMonths] = useState(data.config?.months || 0);

  const operations = [
    { value: 'format', label: 'Format Date' },
    { value: 'extract_year', label: 'Extract Year' },
    { value: 'extract_month', label: 'Extract Month' },
    { value: 'extract_day', label: 'Extract Day' },
    { value: 'day_of_week', label: 'Day of Week' },
    { value: 'add_days', label: 'Add Days' },
    { value: 'add_months', label: 'Add Months' },
  ];

  const commonFormats = [
    { value: '%Y-%m-%d', label: 'YYYY-MM-DD (2024-01-15)' },
    { value: '%d/%m/%Y', label: 'DD/MM/YYYY (15/01/2024)' },
    { value: '%m/%d/%Y', label: 'MM/DD/YYYY (01/15/2024)' },
    { value: '%Y-%m-%d %H:%M:%S', label: 'YYYY-MM-DD HH:MM:SS' },
    { value: '%B %d, %Y', label: 'Month DD, YYYY (January 15, 2024)' },
  ];

  const handleConfigChange = () => {
    data.onConfigChange?.({
      input_format: inputFormat || undefined,
      output_format: outputFormat,
      operation,
      days,
      months
    });
  };

  return (
    <div className={`transform-node date-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon">📅</div>
        <div className="node-title">Date</div>
      </div>
      
      <div className="node-body">
        <button 
          className="config-button"
          onClick={() => setIsConfigOpen(!isConfigOpen)}
        >
          {isConfigOpen ? 'Hide Config' : 'Configure'}
        </button>
        
        {isConfigOpen && (
          <div className="config-panel">
            <div className="config-section">
              <label>Operation</label>
              <select
                value={operation}
                onChange={(e) => {
                  setOperation(e.target.value);
                  handleConfigChange();
                }}
              >
                {operations.map(op => (
                  <option key={op.value} value={op.value}>{op.label}</option>
                ))}
              </select>
            </div>
            
            <div className="config-section">
              <label>Input Format (optional)</label>
              <input
                type="text"
                placeholder="Auto-detect if empty"
                value={inputFormat}
                onChange={(e) => {
                  setInputFormat(e.target.value);
                  handleConfigChange();
                }}
              />
            </div>
            
            {['format', 'add_days', 'add_months'].includes(operation) && (
              <div className="config-section">
                <label>Output Format</label>
                <select
                  value={outputFormat}
                  onChange={(e) => {
                    setOutputFormat(e.target.value);
                    handleConfigChange();
                  }}
                >
                  {commonFormats.map(fmt => (
                    <option key={fmt.value} value={fmt.value}>{fmt.label}</option>
                  ))}
                </select>
              </div>
            )}
            
            {operation === 'add_days' && (
              <div className="config-section">
                <label>Days to Add</label>
                <input
                  type="number"
                  value={days}
                  onChange={(e) => {
                    setDays(Number(e.target.value));
                    handleConfigChange();
                  }}
                />
              </div>
            )}
            
            {operation === 'add_months' && (
              <div className="config-section">
                <label>Months to Add</label>
                <input
                  type="number"
                  value={months}
                  onChange={(e) => {
                    setMonths(Number(e.target.value));
                    handleConfigChange();
                  }}
                />
              </div>
            )}
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default memo(DateNode);
