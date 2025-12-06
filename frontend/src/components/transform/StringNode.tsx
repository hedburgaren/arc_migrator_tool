/**
 * String Transform Node Component
 * Handles string manipulation operations
 */
import { memo, useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import './TransformNode.css';

interface StringConfig {
  operation: string;
  old?: string;
  new?: string;
  start?: number;
  length?: number;
  width?: number;
  fill_char?: string;
}

interface StringNodeData {
  label: string;
  config?: StringConfig;
  onConfigChange?: (config: StringConfig) => void;
}

function StringNode({ data, selected }: NodeProps<StringNodeData>) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [operation, setOperation] = useState(data.config?.operation || 'lowercase');
  const [oldValue, setOldValue] = useState(data.config?.old || '');
  const [newValue, setNewValue] = useState(data.config?.new || '');
  const [start, setStart] = useState(data.config?.start || 0);
  const [length, setLength] = useState(data.config?.length || 10);
  const [width, setWidth] = useState(data.config?.width || 10);
  const [fillChar, setFillChar] = useState(data.config?.fill_char || '0');

  const operations = [
    { value: 'lowercase', label: 'Lowercase' },
    { value: 'uppercase', label: 'Uppercase' },
    { value: 'title', label: 'Title Case' },
    { value: 'trim', label: 'Trim' },
    { value: 'ltrim', label: 'Trim Left' },
    { value: 'rtrim', label: 'Trim Right' },
    { value: 'replace', label: 'Find & Replace' },
    { value: 'substring', label: 'Substring' },
    { value: 'pad_left', label: 'Pad Left' },
    { value: 'pad_right', label: 'Pad Right' },
    { value: 'remove_special', label: 'Remove Special Chars' },
    { value: 'remove_whitespace', label: 'Remove Whitespace' },
    { value: 'normalize_whitespace', label: 'Normalize Whitespace' },
  ];

  const handleConfigChange = () => {
    const config: StringConfig = { operation };
    
    if (operation === 'replace') {
      config.old = oldValue;
      config.new = newValue;
    } else if (operation === 'substring') {
      config.start = start;
      config.length = length;
    } else if (['pad_left', 'pad_right'].includes(operation)) {
      config.width = width;
      config.fill_char = fillChar;
    }
    
    data.onConfigChange?.(config);
  };

  return (
    <div className={`transform-node string-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon">📝</div>
        <div className="node-title">String</div>
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
            
            {operation === 'replace' && (
              <>
                <div className="config-section">
                  <label>Find (old value)</label>
                  <input
                    type="text"
                    value={oldValue}
                    onChange={(e) => {
                      setOldValue(e.target.value);
                      handleConfigChange();
                    }}
                  />
                </div>
                <div className="config-section">
                  <label>Replace with (new value)</label>
                  <input
                    type="text"
                    value={newValue}
                    onChange={(e) => {
                      setNewValue(e.target.value);
                      handleConfigChange();
                    }}
                  />
                </div>
              </>
            )}
            
            {operation === 'substring' && (
              <>
                <div className="config-section">
                  <label>Start Position</label>
                  <input
                    type="number"
                    value={start}
                    onChange={(e) => {
                      setStart(Number(e.target.value));
                      handleConfigChange();
                    }}
                  />
                </div>
                <div className="config-section">
                  <label>Length (0 = to end)</label>
                  <input
                    type="number"
                    value={length}
                    onChange={(e) => {
                      setLength(Number(e.target.value));
                      handleConfigChange();
                    }}
                  />
                </div>
              </>
            )}
            
            {['pad_left', 'pad_right'].includes(operation) && (
              <>
                <div className="config-section">
                  <label>Total Width</label>
                  <input
                    type="number"
                    value={width}
                    onChange={(e) => {
                      setWidth(Number(e.target.value));
                      handleConfigChange();
                    }}
                  />
                </div>
                <div className="config-section">
                  <label>Fill Character</label>
                  <input
                    type="text"
                    maxLength={1}
                    value={fillChar}
                    onChange={(e) => {
                      setFillChar(e.target.value);
                      handleConfigChange();
                    }}
                  />
                </div>
              </>
            )}
            
            <div className="config-info">
              <small>
                {operation === 'lowercase' && 'Converts to lowercase'}
                {operation === 'uppercase' && 'Converts to UPPERCASE'}
                {operation === 'title' && 'Converts To Title Case'}
                {operation === 'trim' && 'Removes leading and trailing spaces'}
                {operation === 'replace' && 'Replaces all occurrences'}
                {operation === 'substring' && 'Extracts a portion of the string'}
                {operation === 'pad_left' && 'Pads on the left with fill character'}
                {operation === 'pad_right' && 'Pads on the right with fill character'}
                {operation === 'remove_special' && 'Keeps only letters, numbers, and spaces'}
                {operation === 'normalize_whitespace' && 'Replaces multiple spaces with single space'}
              </small>
            </div>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default memo(StringNode);
