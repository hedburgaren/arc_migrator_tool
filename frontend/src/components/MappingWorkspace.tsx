/**
 * Main mapping workspace component with ReactFlow
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  Connection,
  Edge,
  Node,
  addEdge,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import SchemaNode from './SchemaNode';
import { SchemaFieldNode, MappingCreate, MappingResponse } from '../types/mapping';
import { FileSchemaResponse } from '../types/schema';
import './MappingWorkspace.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface MappingWorkspaceProps {
  projectId: number;
  sourceFileId: number;
  targetFileId: number;
  sourceSchema: FileSchemaResponse;
  targetSchema: FileSchemaResponse;
  onClose: () => void;
}

function MappingWorkspaceContent({
  projectId,
  sourceFileId,
  targetFileId,
  sourceSchema,
  targetSchema,
  onClose,
}: MappingWorkspaceProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');

  const nodeTypes = useMemo(() => ({ schemaNode: SchemaNode }), []);

  // Generate nodes from schemas
  useEffect(() => {
    const sourceNodes: Node<SchemaFieldNode>[] = sourceSchema.columns.map((col, index) => ({
      id: `source-${col.column_name}-${col.id}`,
      type: 'schemaNode',
      position: { x: 50, y: index * 120 + 50 },
      data: {
        id: `source-${col.column_name}-${col.id}`,
        fieldName: col.column_name,
        dataType: col.data_type,
        sampleValues: col.sample_values || [],
        nullCount: col.null_count,
        uniqueCount: col.unique_count,
        side: 'source',
        fileId: sourceFileId,
      },
    }));

    const targetNodes: Node<SchemaFieldNode>[] = targetSchema.columns.map((col, index) => ({
      id: `target-${col.column_name}-${col.id}`,
      type: 'schemaNode',
      position: { x: 600, y: index * 120 + 50 },
      data: {
        id: `target-${col.column_name}-${col.id}`,
        fieldName: col.column_name,
        dataType: col.data_type,
        sampleValues: col.sample_values || [],
        nullCount: col.null_count,
        uniqueCount: col.unique_count,
        side: 'target',
        fileId: targetFileId,
      },
    }));

    setNodes([...sourceNodes, ...targetNodes]);
  }, [sourceSchema, targetSchema, sourceFileId, targetFileId]);

  const loadMappings = useCallback(async () => {
    if (nodes.length === 0) return; // Wait for nodes to be loaded
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/mappings`);
      if (!response.ok) {
        throw new Error('Failed to load mappings');
      }
      const mappings: MappingResponse[] = await response.json();
      
      // Match edges with actual node IDs using exact field name matching
      const matchedEdges: Edge[] = [];
      
      for (const mapping of mappings) {
        const sourceNode = nodes.find(n => {
          const data = n.data as SchemaFieldNode;
          return data.side === 'source' && data.fieldName === mapping.source_field;
        });
        const targetNode = nodes.find(n => {
          const data = n.data as SchemaFieldNode;
          return data.side === 'target' && data.fieldName === mapping.target_field;
        });
        
        if (sourceNode && targetNode) {
          matchedEdges.push({
            id: `edge-${mapping.id}`,
            source: sourceNode.id,
            target: targetNode.id,
            type: 'default',
            animated: true,
            label: mapping.transform_type,
            labelStyle: { fill: '#666', fontWeight: 500, fontSize: 12 },
            labelBgStyle: { fill: '#fff', fillOpacity: 0.8 },
            data: { 
              mappingId: mapping.id,
              transformType: mapping.transform_type,
            },
          });
        }
      }
      
      setEdges(matchedEdges);
    } catch (err) {
      console.error('Failed to load mappings:', err);
    }
  }, [nodes, projectId]);

  // Load existing mappings after nodes are loaded
  useEffect(() => {
    if (nodes.length > 0) {
      loadMappings();
    }
  }, [nodes, loadMappings]);

  // Validate connection: only allow source -> target connections
  const isValidConnection = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) return false;

      const sourceNode = nodes.find((n) => n.id === connection.source);
      const targetNode = nodes.find((n) => n.id === connection.target);

      if (!sourceNode || !targetNode) return false;

      const sourceData = sourceNode.data as SchemaFieldNode;
      const targetData = targetNode.data as SchemaFieldNode;

      // Only allow source -> target connections (not source -> source or target -> target)
      if (sourceData.side !== 'source' || targetData.side !== 'target') {
        return false;
      }

      // Check if mapping already exists
      const duplicateEdge = edges.find(
        (edge) => edge.source === connection.source && edge.target === connection.target
      );

      return !duplicateEdge;
    },
    [nodes, edges]
  );

  const onConnect = useCallback(
    async (connection: Connection) => {
      if (!connection.source || !connection.target) return;

      const sourceNode = nodes.find((n) => n.id === connection.source);
      const targetNode = nodes.find((n) => n.id === connection.target);

      if (!sourceNode || !targetNode) return;

      const sourceData = sourceNode.data as SchemaFieldNode;
      const targetData = targetNode.data as SchemaFieldNode;

      // Validate connection type
      if (sourceData.side !== 'source' || targetData.side !== 'target') {
        setError('Invalid connection: You can only connect source fields to target fields');
        return;
      }

      // Check for duplicate mapping in UI
      const duplicateEdge = edges.find(
        (edge) => edge.source === connection.source && edge.target === connection.target
      );
      if (duplicateEdge) {
        setError(`Mapping already exists from "${sourceData.fieldName}" to "${targetData.fieldName}"`);
        return;
      }

      // Create mapping in backend
      try {
        setSaving(true);
        setError('');
        
        const mappingData: MappingCreate = {
          source_field: sourceData.fieldName,
          target_field: targetData.fieldName,
          transform_type: '1:1',
        };

        const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/mappings`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(mappingData),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to create mapping');
        }

        const savedMapping: MappingResponse = await response.json();

        // Add edge to the flow with label
        const newEdge: Edge = {
          id: `edge-${savedMapping.id}`,
          source: connection.source,
          target: connection.target,
          type: 'default',
          animated: true,
          label: savedMapping.transform_type,
          labelStyle: { fill: '#666', fontWeight: 500, fontSize: 12 },
          labelBgStyle: { fill: '#fff', fillOpacity: 0.8 },
          data: { 
            mappingId: savedMapping.id,
            transformType: savedMapping.transform_type,
          },
        };

        setEdges((eds) => addEdge(newEdge, eds));
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save mapping');
        console.error('Failed to create mapping:', err);
      } finally {
        setSaving(false);
      }
    },
    [nodes, edges, projectId]
  );

  const onEdgesDelete = useCallback(
    async (deletedEdges: Edge[]) => {
      for (const edge of deletedEdges) {
        if (edge.data?.mappingId) {
          try {
            const response = await fetch(`${API_BASE_URL}/api/mappings/${edge.data.mappingId}`, {
              method: 'DELETE',
            });

            if (!response.ok) {
              console.error('Failed to delete mapping');
            }
          } catch (err) {
            console.error('Failed to delete mapping:', err);
          }
        }
      }
    },
    []
  );

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to clear all mappings?')) {
      return;
    }

    try {
      setSaving(true);
      setError('');

      for (const edge of edges) {
        if (edge.data?.mappingId) {
          await fetch(`${API_BASE_URL}/api/mappings/${edge.data.mappingId}`, {
            method: 'DELETE',
          });
        }
      }

      setEdges([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear mappings');
      console.error('Failed to clear mappings:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mapping-workspace">
      <div className="mapping-workspace-header">
        <div className="header-content">
          <h2>Visual Field Mapping</h2>
          <div className="header-info">
            <span className="schema-label source-label">
              📤 Source: {sourceSchema.filename}
            </span>
            <span className="schema-label target-label">
              📥 Target: {targetSchema.filename}
            </span>
          </div>
        </div>
        <div className="header-actions">
          <button
            className="clear-button"
            onClick={handleClearAll}
            disabled={edges.length === 0 || saving}
          >
            Clear All
          </button>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>
      </div>

      {error && (
        <div className="mapping-error">
          {error}
          <button onClick={() => setError('')}>✕</button>
        </div>
      )}

      {saving && (
        <div className="mapping-saving">
          Saving...
        </div>
      )}

      <div className="mapping-canvas">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onEdgesDelete={onEdgesDelete}
          isValidConnection={isValidConnection}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.1}
          maxZoom={2}
          defaultEdgeOptions={{
            animated: true,
            style: { strokeWidth: 2 },
          }}
        >
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              const data = node.data as SchemaFieldNode;
              return data.side === 'source' ? '#3182ce' : '#38a169';
            }}
            maskColor="rgba(0, 0, 0, 0.1)"
          />
        </ReactFlow>
      </div>

      <div className="mapping-footer">
        <div className="mapping-stats">
          <span>Source Fields: {sourceSchema.column_count}</span>
          <span>Target Fields: {targetSchema.column_count}</span>
          <span>Mappings: {edges.length}</span>
        </div>
        <div className="mapping-help">
          💡 Drag from a source field (left) to a target field (right) to create a mapping. Press Delete/Backspace to remove selected edges.
        </div>
      </div>
    </div>
  );
}

export default function MappingWorkspace(props: MappingWorkspaceProps) {
  return (
    <ReactFlowProvider>
      <MappingWorkspaceContent {...props} />
    </ReactFlowProvider>
  );
}
