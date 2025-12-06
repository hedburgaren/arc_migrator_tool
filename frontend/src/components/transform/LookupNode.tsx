/**
 * Lookup Transform Node Component
 * Maps source values to target values using a lookup table
 */
import { memo, useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import './TransformNode.css';

interface LookupConfig {
  lookup_table: Record<string, string>;
  default_value?: string;
}

interface LookupNodeData {
  label: string;
  config?: LookupConfig;
  onConfigChange?: (config: LookupConfig) => void;
}

function LookupNode({ data, selected }: NodeProps<LookupNodeData>) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [lookupTable, setLookupTable] = useState<Record<string, string>>(
    data.config?.lookup_table || {}
  );
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [defaultValue, setDefaultValue] = useState(data.config?.default_value || '');

  const handleAddMapping = () => {
    if (newKey && newValue) {
      const updated = { ...lookupTable, [newKey]: newValue };
      setLookupTable(updated);
      data.onConfigChange?.({
        lookup_table: updated,
        default_value: defaultValue
      });
      setNewKey('');
      setNewValue('');
    }
  };

  const handleRemoveMapping = (key: string) => {
    const updated = { ...lookupTable };
    delete updated[key];
    setLookupTable(updated);
    data.onConfigChange?.({
      lookup_table: updated,
      default_value: defaultValue
    });
  };

  const handleDefaultValueChange = (value: string) => {
    setDefaultValue(value);
    data.onConfigChange?.({
      lookup_table: lookupTable,
      default_value: value
    });
  };

  return (
    <div className={`transform-node lookup-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon">🔍</div>
        <div className="node-title">Lookup</div>
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
              <label>Lookup Mappings ({Object.keys(lookupTable).length})</label>
              <div className="lookup-list">
                {Object.entries(lookupTable).map(([key, value]) => (
                  <div key={key} className="lookup-item">
                    <span className="lookup-key">{key}</span>
                    <span className="lookup-arrow">→</span>
                    <span className="lookup-value">{value}</span>
                    <button 
                      className="remove-button"
                      onClick={() => handleRemoveMapping(key)}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
              
              <div className="add-mapping">
                <input
                  type="text"
                  placeholder="Source value"
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                />
                <span>→</span>
                <input
                  type="text"
                  placeholder="Target value"
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                />
                <button onClick={handleAddMapping}>Add</button>
              </div>
            </div>
            
            <div className="config-section">
              <label>Default Value (for unmapped)</label>
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

export default memo(LookupNode);
