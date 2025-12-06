/**
 * Conditional Transform Node Component
 * Applies if-then-else logic to transform data
 */
import { memo, useState, useEffect } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import './TransformNode.css';

interface Condition {
  operator: string;
  value: string;
  then_value: string;
}

interface ConditionalConfig {
  conditions: Condition[];
  default_value?: string;
}

interface ConditionalNodeData {
  label: string;
  config?: ConditionalConfig;
  onConfigChange?: (config: ConditionalConfig) => void;
}

function ConditionalNode({ data, selected }: NodeProps<ConditionalNodeData>) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [conditions, setConditions] = useState<Condition[]>(data.config?.conditions || []);
  const [defaultValue, setDefaultValue] = useState(data.config?.default_value || '');

  // Debounced config change
  useEffect(() => {
    const timer = setTimeout(() => {
      data.onConfigChange?.({
        conditions,
        default_value: defaultValue
      });
    }, 500); // Debounce for 500ms
    
    return () => clearTimeout(timer);
  }, [conditions, defaultValue, data]);

  const operators = [
    { value: '==', label: 'Equals' },
    { value: '!=', label: 'Not Equals' },
    { value: '>', label: 'Greater Than' },
    { value: '>=', label: 'Greater or Equal' },
    { value: '<', label: 'Less Than' },
    { value: '<=', label: 'Less or Equal' },
    { value: 'contains', label: 'Contains' },
    { value: 'startswith', label: 'Starts With' },
    { value: 'endswith', label: 'Ends With' },
  ];

  const handleAddCondition = () => {
    const updated = [...conditions, { operator: '==', value: '', then_value: '' }];
    setConditions(updated);
  };

  const handleUpdateCondition = (index: number, field: keyof Condition, value: string) => {
    const updated = [...conditions];
    updated[index] = { ...updated[index], [field]: value };
    setConditions(updated);
  };

  const handleRemoveCondition = (index: number) => {
    const updated = conditions.filter((_, i) => i !== index);
    setConditions(updated);
  };

  const handleDefaultValueChange = (value: string) => {
    setDefaultValue(value);
  };

  return (
    <div className={`transform-node conditional-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon">⚡</div>
        <div className="node-title">Conditional</div>
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
              <label>Conditions ({conditions.length})</label>
              {conditions.map((condition, index) => (
                <div key={index} className="condition-item">
                  <div className="condition-header">
                    <span>If {index + 1}</span>
                    <button 
                      className="remove-button"
                      onClick={() => handleRemoveCondition(index)}
                    >
                      ×
                    </button>
                  </div>
                  <div className="condition-config">
                    <select
                      value={condition.operator}
                      onChange={(e) => handleUpdateCondition(index, 'operator', e.target.value)}
                    >
                      {operators.map(op => (
                        <option key={op.value} value={op.value}>{op.label}</option>
                      ))}
                    </select>
                    <input
                      type="text"
                      placeholder="Value"
                      value={condition.value}
                      onChange={(e) => handleUpdateCondition(index, 'value', e.target.value)}
                    />
                    <span>→</span>
                    <input
                      type="text"
                      placeholder="Then"
                      value={condition.then_value}
                      onChange={(e) => handleUpdateCondition(index, 'then_value', e.target.value)}
                    />
                  </div>
                </div>
              ))}
              <button className="add-button" onClick={handleAddCondition}>
                + Add Condition
              </button>
            </div>
            
            <div className="config-section">
              <label>Default Value (else)</label>
              <input
                type="text"
                placeholder="Default value"
                value={defaultValue}
                onChange={(e) => handleDefaultValueChange(e.target.value)}
              />
            </div>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default memo(ConditionalNode);
