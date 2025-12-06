/**
 * Math Transform Node Component
 * Performs mathematical operations on numeric data
 */
import { memo, useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import './TransformNode.css';

interface MathConfig {
  operation: string;
  operand?: number;
  source_fields?: string[];
}

interface MathNodeData {
  label: string;
  config?: MathConfig;
  onConfigChange?: (config: MathConfig) => void;
}

function MathNode({ data, selected }: NodeProps<MathNodeData>) {
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [operation, setOperation] = useState(data.config?.operation || 'add');
  const [operand, setOperand] = useState(data.config?.operand || 0);

  const singleOperations = [
    { value: 'add', label: 'Add (+)' },
    { value: 'subtract', label: 'Subtract (−)' },
    { value: 'multiply', label: 'Multiply (×)' },
    { value: 'divide', label: 'Divide (÷)' },
    { value: 'round', label: 'Round' },
    { value: 'abs', label: 'Absolute Value' },
    { value: 'ceil', label: 'Ceiling' },
    { value: 'floor', label: 'Floor' },
  ];

  const multiOperations = [
    { value: 'sum', label: 'Sum' },
    { value: 'average', label: 'Average' },
    { value: 'min', label: 'Minimum' },
    { value: 'max', label: 'Maximum' },
  ];

  const handleOperationChange = (value: string) => {
    setOperation(value);
    data.onConfigChange?.({
      operation: value,
      operand
    });
  };

  const handleOperandChange = (value: number) => {
    setOperand(value);
    data.onConfigChange?.({
      operation,
      operand: value
    });
  };

  return (
    <div className={`transform-node math-node ${selected ? 'selected' : ''}`}>
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon">🔢</div>
        <div className="node-title">Math</div>
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
                onChange={(e) => handleOperationChange(e.target.value)}
              >
                <optgroup label="Single Field">
                  {singleOperations.map(op => (
                    <option key={op.value} value={op.value}>{op.label}</option>
                  ))}
                </optgroup>
                <optgroup label="Multiple Fields">
                  {multiOperations.map(op => (
                    <option key={op.value} value={op.value}>{op.label}</option>
                  ))}
                </optgroup>
              </select>
            </div>
            
            {['add', 'subtract', 'multiply', 'divide', 'round'].includes(operation) && (
              <div className="config-section">
                <label>
                  {operation === 'round' ? 'Decimal Places' : 'Operand'}
                </label>
                <input
                  type="number"
                  value={operand}
                  onChange={(e) => handleOperandChange(Number(e.target.value))}
                  step={operation === 'round' ? 1 : 0.01}
                />
              </div>
            )}
            
            <div className="config-info">
              <small>
                {operation === 'add' && 'Adds a number to each value'}
                {operation === 'subtract' && 'Subtracts a number from each value'}
                {operation === 'multiply' && 'Multiplies each value by a number'}
                {operation === 'divide' && 'Divides each value by a number'}
                {operation === 'round' && 'Rounds to specified decimal places'}
                {operation === 'abs' && 'Returns absolute value'}
                {operation === 'ceil' && 'Rounds up to nearest integer'}
                {operation === 'floor' && 'Rounds down to nearest integer'}
                {operation === 'sum' && 'Sums multiple fields'}
                {operation === 'average' && 'Averages multiple fields'}
                {operation === 'min' && 'Returns minimum of multiple fields'}
                {operation === 'max' && 'Returns maximum of multiple fields'}
              </small>
            </div>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default memo(MathNode);
