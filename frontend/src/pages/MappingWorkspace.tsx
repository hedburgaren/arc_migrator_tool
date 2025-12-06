import { useState, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { mappingApi, schemaApi, fileApi, executionApi } from '../services/api'
import MappingEditor from '../components/MappingEditor'
import PreviewDashboard from '../components/PreviewDashboard'
import { ArrowLeft, Play, Eye, Loader } from 'lucide-react'
import type { MappingEdgeCreate } from '../types'

type View = 'editor' | 'preview'

export default function MappingWorkspace() {
  const { projectId, profileId } = useParams<{ projectId: string; profileId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeView, setActiveView] = useState<View>('editor')

  const projectIdNum = parseInt(projectId || '0')
  const profileIdNum = parseInt(profileId || '0')

  // Queries
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['mapping', profileIdNum],
    queryFn: () => mappingApi.get(profileIdNum),
    enabled: !!profileIdNum,
  })

  const { data: sourceSchema } = useQuery({
    queryKey: ['schema', profile?.source_schema_id],
    queryFn: () => schemaApi.get(profile!.source_schema_id!),
    enabled: !!profile?.source_schema_id,
  })

  const { data: targetSchema } = useQuery({
    queryKey: ['schema', profile?.target_schema_id],
    queryFn: () => schemaApi.get(profile!.target_schema_id!),
    enabled: !!profile?.target_schema_id,
  })

  const { data: files = [] } = useQuery({
    queryKey: ['files', projectIdNum],
    queryFn: () => fileApi.listByProject(projectIdNum),
    enabled: !!projectIdNum,
  })

  const [previewData, setPreviewData] = useState<{
    source_data: Record<string, unknown>[]
    transformed_data: Record<string, unknown>[]
    warnings: Array<{ type: string; message: string; row_index?: number; target_field?: string }>
    warnings_count: number
  } | null>(null)

  // Mutations
  const addEdgeMutation = useMutation({
    mutationFn: (edge: MappingEdgeCreate) => mappingApi.addEdge(profileIdNum, edge),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mapping', profileIdNum] })
    },
  })

  const deleteEdgeMutation = useMutation({
    mutationFn: (edgeId: number) => mappingApi.deleteEdge(profileIdNum, edgeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mapping', profileIdNum] })
    },
  })

  const previewMutation = useMutation({
    mutationFn: ({ fileId }: { fileId: number }) =>
      mappingApi.preview(profileIdNum, fileId, 20),
    onSuccess: (data) => {
      setPreviewData(data)
      setActiveView('preview')
    },
  })

  const executeMutation = useMutation({
    mutationFn: ({ fileId, mode }: { fileId: number; mode: 'preview' | 'dry_run' | 'commit' }) =>
      executionApi.execute(profileIdNum, fileId, mode),
    onSuccess: (execution) => {
      navigate(`/projects/${projectIdNum}/execution/${execution.id}`)
    },
  })

  const handleEdgeCreate = useCallback(
    (sourceFieldId: number, targetFieldId: number) => {
      addEdgeMutation.mutate({
        source_field_id: sourceFieldId,
        target_field_id: targetFieldId,
        mapping_type: 'direct',
        transform_type: 'none',
      })
    },
    [addEdgeMutation]
  )

  const handleEdgeDelete = useCallback(
    (edgeId: number) => {
      deleteEdgeMutation.mutate(edgeId)
    },
    [deleteEdgeMutation]
  )

  const handlePreview = () => {
    const sourceFile = files.find((f) => f.id)
    if (sourceFile) {
      previewMutation.mutate({ fileId: sourceFile.id })
    }
  }

  const handleExecute = (mode: 'preview' | 'dry_run' | 'commit') => {
    const sourceFile = files.find((f) => f.id)
    if (sourceFile) {
      executeMutation.mutate({ fileId: sourceFile.id, mode })
    }
  }

  if (profileLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Mapping profile not found</p>
        <Link to={`/projects/${projectIdNum}`} className="text-primary-600 hover:underline mt-2 inline-block">
          Return to Project
        </Link>
      </div>
    )
  }

  const sourceFields = sourceSchema?.fields || []
  const targetFields = targetSchema?.fields || []

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <Link
            to={`/projects/${projectIdNum}`}
            className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Link>
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              {profile.name}
            </h1>
            <p className="text-sm text-gray-500">Version {profile.version}</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* View toggle */}
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setActiveView('editor')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'editor'
                  ? 'bg-white dark:bg-gray-600 shadow text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              Editor
            </button>
            <button
              onClick={() => setActiveView('preview')}
              className={`px-3 py-1 text-sm rounded ${
                activeView === 'preview'
                  ? 'bg-white dark:bg-gray-600 shadow text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              Preview
            </button>
          </div>

          {/* Actions */}
          <button
            onClick={handlePreview}
            disabled={previewMutation.isPending || files.length === 0}
            className="flex items-center px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 disabled:opacity-50"
          >
            <Eye className="w-4 h-4 mr-2" />
            Preview
          </button>
          <button
            onClick={() => handleExecute('dry_run')}
            disabled={executeMutation.isPending || files.length === 0}
            className="flex items-center px-3 py-2 text-sm bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 disabled:opacity-50"
          >
            <Play className="w-4 h-4 mr-2" />
            Dry Run
          </button>
          <button
            onClick={() => handleExecute('commit')}
            disabled={executeMutation.isPending || files.length === 0}
            className="flex items-center px-3 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            <Play className="w-4 h-4 mr-2" />
            Execute
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeView === 'editor' ? (
          sourceFields.length > 0 && targetFields.length > 0 ? (
            <MappingEditor
              sourceFields={sourceFields}
              targetFields={targetFields}
              mappingEdges={profile.edges || []}
              onEdgeCreate={handleEdgeCreate}
              onEdgeDelete={handleEdgeDelete}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {sourceFields.length === 0
                    ? 'No source schema available. Please discover a schema first.'
                    : 'No target schema available. Please create or discover a target schema.'}
                </p>
                <Link
                  to={`/projects/${projectIdNum}`}
                  className="text-primary-600 hover:underline"
                >
                  Go to project settings
                </Link>
              </div>
            </div>
          )
        ) : previewData ? (
          <div className="p-6 overflow-auto h-full">
            <PreviewDashboard
              sourceData={previewData.source_data}
              transformedData={previewData.transformed_data}
              warnings={previewData.warnings}
              warningsCount={previewData.warnings_count}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Click "Preview" to see how your data will be transformed
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
