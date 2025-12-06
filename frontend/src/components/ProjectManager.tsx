/**
 * Project manager component for creating projects and launching mapping workspace
 */
import { useState, useEffect } from 'react';
import { FileMetadata } from '../types/file';
import { FileSchemaResponse } from '../types/schema';
import { createProject, listProjects, ProjectResponse, getFileSchema } from '../services/api';
import MappingWorkspace from './MappingWorkspace';
import './ProjectManager.css';

interface ProjectManagerProps {
  files: FileMetadata[];
}

export default function ProjectManager({ files }: ProjectManagerProps) {
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  
  // New project form
  const [projectName, setProjectName] = useState('');
  const [sourceFileId, setSourceFileId] = useState<number | null>(null);
  const [targetFileId, setTargetFileId] = useState<number | null>(null);
  
  // Mapping workspace state
  const [activeProject, setActiveProject] = useState<{
    project: ProjectResponse;
    sourceFileId: number;
    targetFileId: number;
    sourceSchema: FileSchemaResponse;
    targetSchema: FileSchemaResponse;
  } | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError('');
      const projectList = await listProjects();
      setProjects(projectList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    if (!projectName.trim()) {
      setError('Project name is required');
      return;
    }
    if (!sourceFileId || !targetFileId) {
      setError('Please select both source and target files');
      return;
    }
    if (sourceFileId === targetFileId) {
      setError('Source and target files must be different');
      return;
    }

    try {
      setCreating(true);
      setError('');

      const sourceFile = files.find(f => f.id === sourceFileId);
      const targetFile = files.find(f => f.id === targetFileId);

      await createProject({
        name: projectName,
        description: `Mapping from ${sourceFile?.filename} to ${targetFile?.filename}`,
        source_system: sourceFile?.filename,
        target_system: targetFile?.filename,
        status: 'draft',
      });

      await loadProjects();
      setShowCreateDialog(false);
      setProjectName('');
      setSourceFileId(null);
      setTargetFileId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const handleOpenMapping = async (project: ProjectResponse) => {
    try {
      setError('');
      
      // Find files based on project metadata
      const sourceFile = files.find(f => f.filename === project.source_system);
      const targetFile = files.find(f => f.filename === project.target_system);
      
      if (!sourceFile || !targetFile) {
        setError('Could not find source or target files for this project');
        return;
      }

      // Check if schemas are analyzed
      if (!sourceFile.schema_analyzed || !targetFile.schema_analyzed) {
        setError('Please analyze schemas for both files before mapping');
        return;
      }

      // Load schemas
      const sourceSchema = await getFileSchema(sourceFile.id);
      const targetSchema = await getFileSchema(targetFile.id);

      setActiveProject({
        project,
        sourceFileId: sourceFile.id,
        targetFileId: targetFile.id,
        sourceSchema,
        targetSchema,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open mapping workspace');
    }
  };

  const analyzedFiles = files.filter(f => f.schema_analyzed);

  if (activeProject) {
    return (
      <MappingWorkspace
        projectId={activeProject.project.id}
        sourceFileId={activeProject.sourceFileId}
        targetFileId={activeProject.targetFileId}
        sourceSchema={activeProject.sourceSchema}
        targetSchema={activeProject.targetSchema}
        onClose={() => setActiveProject(null)}
      />
    );
  }

  return (
    <div className="project-manager">
      <div className="project-manager-header">
        <h2>Mapping Projects</h2>
        <button
          className="create-project-btn"
          onClick={() => setShowCreateDialog(true)}
          disabled={analyzedFiles.length < 2}
        >
          + New Project
        </button>
      </div>

      {error && (
        <div className="project-error">
          {error}
          <button onClick={() => setError('')}>✕</button>
        </div>
      )}

      {analyzedFiles.length < 2 && (
        <div className="project-notice">
          ℹ️ You need at least 2 analyzed files to create a mapping project.
          Upload and analyze files first.
        </div>
      )}

      {loading ? (
        <div className="project-loading">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="project-empty">
          <p>No projects yet. Create a new project to start mapping fields.</p>
        </div>
      ) : (
        <div className="project-list">
          {projects.map(project => (
            <div key={project.id} className="project-card">
              <div className="project-info">
                <h3>{project.name}</h3>
                {project.description && (
                  <p className="project-description">{project.description}</p>
                )}
                <div className="project-meta">
                  <span className="project-status">{project.status}</span>
                  <span className="project-date">
                    Created: {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="project-actions">
                <button
                  className="open-mapping-btn"
                  onClick={() => handleOpenMapping(project)}
                >
                  🗺️ Open Mapping
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateDialog && (
        <div className="dialog-overlay">
          <div className="dialog-content">
            <div className="dialog-header">
              <h3>Create New Project</h3>
              <button
                className="dialog-close"
                onClick={() => {
                  setShowCreateDialog(false);
                  setProjectName('');
                  setSourceFileId(null);
                  setTargetFileId(null);
                  setError('');
                }}
              >
                ✕
              </button>
            </div>

            <div className="dialog-body">
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="My Migration Project"
                  disabled={creating}
                />
              </div>

              <div className="form-group">
                <label>Source File</label>
                <select
                  value={sourceFileId || ''}
                  onChange={(e) => setSourceFileId(Number(e.target.value))}
                  disabled={creating}
                >
                  <option value="">Select source file...</option>
                  {analyzedFiles.map(file => (
                    <option key={file.id} value={file.id}>
                      {file.filename} ({file.column_count} columns)
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Target File</label>
                <select
                  value={targetFileId || ''}
                  onChange={(e) => setTargetFileId(Number(e.target.value))}
                  disabled={creating}
                >
                  <option value="">Select target file...</option>
                  {analyzedFiles.map(file => (
                    <option key={file.id} value={file.id}>
                      {file.filename} ({file.column_count} columns)
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="dialog-footer">
              <button
                className="btn-cancel"
                onClick={() => {
                  setShowCreateDialog(false);
                  setProjectName('');
                  setSourceFileId(null);
                  setTargetFileId(null);
                  setError('');
                }}
                disabled={creating}
              >
                Cancel
              </button>
              <button
                className="btn-create"
                onClick={handleCreateProject}
                disabled={creating}
              >
                {creating ? 'Creating...' : 'Create Project'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
