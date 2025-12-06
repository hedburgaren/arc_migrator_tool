import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectApi, fileApi, schemaApi, mappingApi } from '../services/api'
import FileUpload from '../components/FileUpload'
import SchemaView from '../components/SchemaView'
import {
  ArrowLeft,
  Upload,
  Database,
  Map,
  Play,
  Loader,
  Plus,
  Trash2,
  Eye,
} from 'lucide-react'

type Tab = 'files' | 'schemas' | 'mappings' | 'executions'

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<Tab>('files')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const projectIdNum = parseInt(projectId || '0')

  // Queries
  const { data: project, isLoading: projectLoading } = useQuery({
    queryKey: ['project', projectIdNum],
    queryFn: () => projectApi.get(projectIdNum),
    enabled: !!projectIdNum,
  })

  const { data: files = [] } = useQuery({
    queryKey: ['files', projectIdNum],
    queryFn: () => fileApi.listByProject(projectIdNum),
    enabled: !!projectIdNum,
  })

  const { data: schemas = [] } = useQuery({
    queryKey: ['schemas', projectIdNum],
    queryFn: () => schemaApi.listByProject(projectIdNum),
    enabled: !!projectIdNum,
  })

  const { data: mappings = [] } = useQuery({
    queryKey: ['mappings', projectIdNum],
    queryFn: () => mappingApi.listByProject(projectIdNum),
    enabled: !!projectIdNum,
  })

  // Mutations
  const uploadMutation = useMutation({
    mutationFn: (file: File) => fileApi.upload(projectIdNum, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files', projectIdNum] })
      setSelectedFile(null)
      setIsUploading(false)
    },
    onError: () => {
      setIsUploading(false)
    },
  })

  const discoverSchemaMutation = useMutation({
    mutationFn: ({ fileId, name }: { fileId: number; name: string }) =>
      schemaApi.discoverFromFile(fileId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schemas', projectIdNum] })
    },
  })

  const createMappingMutation = useMutation({
    mutationFn: (data: { name: string; source_schema_id?: number; target_schema_id?: number }) =>
      mappingApi.create(projectIdNum, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mappings', projectIdNum] })
    },
  })

  const deleteFileMutation = useMutation({
    mutationFn: fileApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files', projectIdNum] })
    },
  })

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
  }

  const handleFileRemove = () => {
    setSelectedFile(null)
  }

  const handleUpload = () => {
    if (selectedFile) {
      setIsUploading(true)
      uploadMutation.mutate(selectedFile)
    }
  }

  const handleDiscoverSchema = (fileId: number, fileName: string) => {
    const name = fileName.replace(/\.[^/.]+$/, '') // Remove extension
    discoverSchemaMutation.mutate({ fileId, name })
  }

  const handleCreateMapping = () => {
    const sourceSchema = schemas.find((s) => s.schema_type === 'source')
    const targetSchema = schemas.find((s) => s.schema_type === 'target')

    createMappingMutation.mutate({
      name: `Mapping ${mappings.length + 1}`,
      source_schema_id: sourceSchema?.id,
      target_schema_id: targetSchema?.id,
    })
  }

  if (projectLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Project not found</p>
        <Link to="/" className="text-primary-600 hover:underline mt-2 inline-block">
          Return to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {project.name}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {project.source_system} → {project.target_system}
            </p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              project.status === 'completed'
                ? 'bg-green-100 text-green-700'
                : project.status === 'failed'
                ? 'bg-red-100 text-red-700'
                : 'bg-gray-100 text-gray-700'
            }`}
          >
            {project.status}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'files' as Tab, label: 'Files', icon: Upload },
            { id: 'schemas' as Tab, label: 'Schemas', icon: Database },
            { id: 'mappings' as Tab, label: 'Mappings', icon: Map },
            { id: 'executions' as Tab, label: 'Executions', icon: Play },
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === 'files' && (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Upload Data File
            </h2>
            <FileUpload
              onFileSelect={handleFileSelect}
              onFileRemove={handleFileRemove}
              selectedFile={selectedFile}
              isUploading={isUploading}
            />
            {selectedFile && !isUploading && (
              <button
                onClick={handleUpload}
                className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Upload File
              </button>
            )}
          </div>

          {/* Uploaded files list */}
          {files.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Uploaded Files
                </h2>
              </div>
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {files.map((file) => (
                  <div
                    key={file.id}
                    className="px-6 py-4 flex items-center justify-between"
                  >
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {file.original_filename}
                      </p>
                      <p className="text-sm text-gray-500">
                        {file.row_count} rows, {file.column_count} columns
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() =>
                          handleDiscoverSchema(file.id, file.original_filename)
                        }
                        disabled={discoverSchemaMutation.isPending}
                        className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                      >
                        <Database className="w-4 h-4 inline mr-1" />
                        Discover Schema
                      </button>
                      <button
                        onClick={() => deleteFileMutation.mutate(file.id)}
                        className="p-1 text-gray-400 hover:text-red-500"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'schemas' && (
        <div className="space-y-6">
          {schemas.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <Database className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                No schemas discovered yet. Upload a file and discover its schema.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-6">
              {schemas.map((schema) => (
                <SchemaView
                  key={schema.id}
                  name={schema.name}
                  fields={(schema as any).fields || []}
                  type={schema.schema_type}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'mappings' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Mapping Profiles
            </h2>
            <button
              onClick={handleCreateMapping}
              disabled={schemas.length < 1}
              className={`flex items-center px-4 py-2 rounded-lg ${
                schemas.length >= 1
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              <Plus className="w-4 h-4 mr-2" />
              New Mapping
            </button>
          </div>

          {mappings.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <Map className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">
                No mapping profiles yet. Create one to start mapping fields.
              </p>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm divide-y divide-gray-200 dark:divide-gray-700">
              {mappings.map((mapping) => (
                <div
                  key={mapping.id}
                  className="px-6 py-4 flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {mapping.name}
                    </p>
                    <p className="text-sm text-gray-500">Version {mapping.version}</p>
                  </div>
                  <Link
                    to={`/projects/${projectIdNum}/mapping/${mapping.id}`}
                    className="flex items-center px-3 py-1 text-sm bg-primary-100 text-primary-700 rounded hover:bg-primary-200"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    Open Editor
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'executions' && (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
          <Play className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Execution history will appear here after running migrations.
          </p>
        </div>
      )}
    </div>
  )
}
