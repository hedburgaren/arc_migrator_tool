/**
 * Custom Transform Node Component
 * Placeholder for user-defined transformations
 */
import { memo, useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import './TransformNode.css';

interface CustomConfig {
  function_code?: string;
  description?: string;
}

interface CustomNodeData {
  label: string;
  config?: CustomConfig;
  onConfigChange?: (config: CustomConfig) => void;
}

function CustomNode({ data, selected }: NodeProps<CustomNodeData>) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [description, setDescription] = useState(data.config?.description || '');
  const [functionCode, setFunctionCode] = useState(data.config?.function_code || '');

  const handleConfigChange = () => {
    data.onConfigChange?.({
      description,
      function_code: functionCode
    });
  };

  return (
    <div className={`transform-node custom-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon">⚙️</div>
        <div className="node-title">Custom</div>
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
              <label>Description</label>
              <input
                type="text"
                placeholder="What does this transform do?"
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                  handleConfigChange();
                }}
              />
            </div>
            
            <div className="config-section">
              <label>Custom Function</label>
              <textarea
                placeholder="def transform(value):\n    # Your code here\n    return value"
                value={functionCode}
                onChange={(e) => {
                  setFunctionCode(e.target.value);
                  handleConfigChange();
                }}
                rows={6}
                style={{ fontFamily: 'monospace', fontSize: '12px' }}
              />
              <small className="warning">
                ⚠️ Custom functions are not yet implemented. This is a placeholder for future functionality.
              </small>
            </div>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default memo(CustomNode);
