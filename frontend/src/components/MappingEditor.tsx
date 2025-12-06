import { useMemo, useCallback, useState } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Connection,
  MarkerType,
  Handle,
  Position,
  NodeProps,
} from 'reactflow'
import 'reactflow/dist/style.css'
import type { FieldDefinition, MappingEdge } from '../types'
import { Trash2 } from 'lucide-react'

interface MappingEditorProps {
  sourceFields: FieldDefinition[]
  targetFields: FieldDefinition[]
  mappingEdges: MappingEdge[]
  onEdgeCreate: (sourceFieldId: number, targetFieldId: number) => void
  onEdgeDelete: (edgeId: number) => void
  onEdgeUpdate?: (edgeId: number, config: Partial<MappingEdge>) => void
}

// Custom node component for fields
function FieldNode({ data, isConnectable }: NodeProps) {
  return (
    <div
      className={`px-3 py-2 rounded-lg border-2 min-w-40 ${
        data.type === 'source'
          ? 'bg-blue-50 border-blue-300 dark:bg-blue-900/30 dark:border-blue-600'
          : 'bg-green-50 border-green-300 dark:bg-green-900/30 dark:border-green-600'
      }`}
    >
      {data.type === 'source' && (
        <Handle
          type="source"
          position={Position.Right}
          isConnectable={isConnectable}
          className="w-3 h-3 bg-blue-500"
        />
      )}
      {data.type === 'target' && (
        <Handle
          type="target"
          position={Position.Left}
          isConnectable={isConnectable}
          className="w-3 h-3 bg-green-500"
        />
      )}
      <div className="text-sm font-medium text-gray-900 dark:text-white">
        {data.displayName || data.name}
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-1">
        <span>{data.fieldType}</span>
        {data.isRequired && <span className="text-red-500">*</span>}
      </div>
    </div>
  )
}

const nodeTypes = {
  field: FieldNode,
}

export default function MappingEditor({
  sourceFields,
  targetFields,
  mappingEdges,
  onEdgeCreate,
  onEdgeDelete,
}: MappingEditorProps) {
  const [selectedEdgeId, setSelectedEdgeId] = useState<number | null>(null)

  // Generate nodes from fields
  const initialNodes: Node[] = useMemo(() => {
    const sourceNodes: Node[] = sourceFields.map((field, index) => ({
      id: `source-${field.id}`,
      type: 'field',
      position: { x: 50, y: 50 + index * 80 },
      data: {
        type: 'source',
        name: field.name,
        displayName: field.display_name,
        fieldType: field.field_type,
        isRequired: field.is_required,
        fieldId: field.id,
      },
    }))

    const targetNodes: Node[] = targetFields.map((field, index) => ({
      id: `target-${field.id}`,
      type: 'field',
      position: { x: 500, y: 50 + index * 80 },
      data: {
        type: 'target',
        name: field.name,
        displayName: field.display_name,
        fieldType: field.field_type,
        isRequired: field.is_required,
        fieldId: field.id,
      },
    }))

    return [...sourceNodes, ...targetNodes]
  }, [sourceFields, targetFields])

  // Generate edges from mapping edges
  const initialEdges: Edge[] = useMemo(() => {
    return mappingEdges
      .filter((edge) => edge.source_field_id !== null)
      .map((edge) => ({
        id: `edge-${edge.id}`,
        source: `source-${edge.source_field_id}`,
        target: `target-${edge.target_field_id}`,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#6366f1',
        },
        style: { stroke: '#6366f1', strokeWidth: 2 },
        data: { mappingEdgeId: edge.id },
      }))
  }, [mappingEdges])

  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (connection: Connection) => {
      // Extract field IDs from node IDs
      const sourceId = connection.source?.replace('source-', '')
      const targetId = connection.target?.replace('target-', '')

      if (sourceId && targetId) {
        onEdgeCreate(parseInt(sourceId), parseInt(targetId))
      }
    },
    [onEdgeCreate]
  )

  const onEdgeClick = useCallback(
    (_: React.MouseEvent, edge: Edge) => {
      const mappingEdgeId = edge.data?.mappingEdgeId
      if (mappingEdgeId) {
        setSelectedEdgeId(mappingEdgeId)
      }
    },
    []
  )

  const handleDeleteSelected = useCallback(() => {
    if (selectedEdgeId !== null) {
      onEdgeDelete(selectedEdgeId)
      setSelectedEdgeId(null)
    }
  }, [selectedEdgeId, onEdgeDelete])

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="text-sm text-gray-600 dark:text-gray-300">
          Draw connections from source fields (left) to target fields (right)
        </div>
        <div className="flex items-center space-x-2">
          {selectedEdgeId !== null && (
            <>
              <button
                onClick={handleDeleteSelected}
                className="flex items-center px-3 py-1 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      {/* Flow canvas */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onEdgeClick={onEdgeClick}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-right"
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
    </div>
  )
}
