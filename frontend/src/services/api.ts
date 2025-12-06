import axios from 'axios'
import type {
  Project,
  ProjectCreate,
  ProjectListResponse,
  SourceFile,
  FilePreview,
  SchemaWithFields,
  MappingProfile,
  MappingProfileWithEdges,
  MappingEdgeCreate,
  MappingEdge,
  MappingPreviewResponse,
  ExecutionRun,
  ExecutionWithLogs,
  ExecutionMode,
} from '../types'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Project API
export const projectApi = {
  list: async (): Promise<ProjectListResponse> => {
    const { data } = await api.get<ProjectListResponse>('/projects')
    return data
  },

  get: async (id: number): Promise<Project> => {
    const { data } = await api.get<Project>(`/projects/${id}`)
    return data
  },

  create: async (project: ProjectCreate): Promise<Project> => {
    const { data } = await api.post<Project>('/projects', project)
    return data
  },

  update: async (id: number, project: Partial<ProjectCreate>): Promise<Project> => {
    const { data } = await api.put<Project>(`/projects/${id}`, project)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/projects/${id}`)
  },

  getSummary: async (id: number) => {
    const { data } = await api.get(`/projects/${id}/summary`)
    return data
  },
}

// File API
export const fileApi = {
  upload: async (projectId: number, file: File, sheetName?: string): Promise<SourceFile> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const params = new URLSearchParams()
    if (sheetName) {
      params.append('sheet_name', sheetName)
    }
    
    const { data } = await api.post<SourceFile>(
      `/files/upload/${projectId}${params.toString() ? '?' + params.toString() : ''}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return data
  },

  listByProject: async (projectId: number): Promise<SourceFile[]> => {
    const { data } = await api.get<SourceFile[]>(`/files/project/${projectId}`)
    return data
  },

  get: async (id: number): Promise<SourceFile> => {
    const { data } = await api.get<SourceFile>(`/files/${id}`)
    return data
  },

  getPreview: async (id: number, rows = 100): Promise<FilePreview> => {
    const { data } = await api.get<FilePreview>(`/files/${id}/preview?rows=${rows}`)
    return data
  },

  getSheets: async (id: number): Promise<{ file_id: number; sheets: string[] }> => {
    const { data } = await api.get(`/files/${id}/sheets`)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/files/${id}`)
  },
}

// Schema API
export const schemaApi = {
  discoverFromFile: async (
    fileId: number,
    name: string,
    systemType = 'csv'
  ): Promise<SchemaWithFields> => {
    const { data } = await api.post<SchemaWithFields>('/schemas/discover', {
      file_id: fileId,
      name,
      system_type: systemType,
    })
    return data
  },

  create: async (
    projectId: number,
    schema: { name: string; schema_type: 'source' | 'target'; system_type: string; description?: string }
  ): Promise<SchemaWithFields> => {
    const { data } = await api.post<SchemaWithFields>(`/schemas/project/${projectId}`, schema)
    return data
  },

  listByProject: async (projectId: number, schemaType?: 'source' | 'target'): Promise<SchemaWithFields[]> => {
    const params = schemaType ? `?schema_type=${schemaType}` : ''
    const { data } = await api.get<SchemaWithFields[]>(`/schemas/project/${projectId}${params}`)
    return data
  },

  get: async (id: number): Promise<SchemaWithFields> => {
    const { data } = await api.get<SchemaWithFields>(`/schemas/${id}`)
    return data
  },

  addField: async (
    schemaId: number,
    field: { name: string; display_name?: string; field_type?: string; is_required?: boolean; position?: number }
  ) => {
    const { data } = await api.post(`/schemas/${schemaId}/fields`, field)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/schemas/${id}`)
  },

  getLookupCandidates: async (id: number) => {
    const { data } = await api.get(`/schemas/${id}/lookup-candidates`)
    return data
  },
}

// Mapping API
export const mappingApi = {
  create: async (
    projectId: number,
    profile: { name: string; description?: string; source_schema_id?: number; target_schema_id?: number }
  ): Promise<MappingProfile> => {
    const { data } = await api.post<MappingProfile>(`/mappings/project/${projectId}`, profile)
    return data
  },

  listByProject: async (projectId: number): Promise<MappingProfile[]> => {
    const { data } = await api.get<MappingProfile[]>(`/mappings/project/${projectId}`)
    return data
  },

  get: async (id: number): Promise<MappingProfileWithEdges> => {
    const { data } = await api.get<MappingProfileWithEdges>(`/mappings/${id}`)
    return data
  },

  addEdge: async (profileId: number, edge: MappingEdgeCreate): Promise<MappingEdge> => {
    const { data } = await api.post<MappingEdge>(`/mappings/${profileId}/edges`, edge)
    return data
  },

  updateEdge: async (profileId: number, edgeId: number, edge: MappingEdgeCreate): Promise<MappingEdge> => {
    const { data } = await api.put<MappingEdge>(`/mappings/${profileId}/edges/${edgeId}`, edge)
    return data
  },

  deleteEdge: async (profileId: number, edgeId: number): Promise<void> => {
    await api.delete(`/mappings/${profileId}/edges/${edgeId}`)
  },

  updateLayout: async (profileId: number, layout: Record<string, unknown>): Promise<MappingProfile> => {
    const { data } = await api.put<MappingProfile>(`/mappings/${profileId}/layout`, { layout_json: layout })
    return data
  },

  preview: async (profileId: number, fileId: number, rows = 10): Promise<MappingPreviewResponse> => {
    const { data } = await api.post<MappingPreviewResponse>(
      `/mappings/${profileId}/preview?file_id=${fileId}&rows=${rows}`
    )
    return data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/mappings/${id}`)
  },
}

// Execution API
export const executionApi = {
  execute: async (
    mappingProfileId: number,
    fileId: number,
    mode: ExecutionMode
  ): Promise<ExecutionRun> => {
    const { data } = await api.post<ExecutionRun>('/executions/execute', {
      mapping_profile_id: mappingProfileId,
      file_id: fileId,
      mode,
    })
    return data
  },

  listByProject: async (projectId: number): Promise<ExecutionRun[]> => {
    const { data } = await api.get<ExecutionRun[]>(`/executions/project/${projectId}`)
    return data
  },

  get: async (id: number): Promise<ExecutionWithLogs> => {
    const { data } = await api.get<ExecutionWithLogs>(`/executions/${id}`)
    return data
  },

  getOutputFiles: async (id: number): Promise<{ execution_id: number; status: string; output_files: string[] }> => {
    const { data } = await api.get(`/executions/${id}/output-files`)
    return data
  },
}

// Health API
export const healthApi = {
  check: async (): Promise<{ status: string; service: string }> => {
    const { data } = await api.get('/health')
    return data
  },
}

export default api
