import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { projectApi } from '../services/api'
import { FolderPlus, ChevronRight, Clock, CheckCircle, AlertCircle, Loader } from 'lucide-react'

const statusIcons = {
  draft: Clock,
  mapping: Loader,
  ready: CheckCircle,
  executing: Loader,
  completed: CheckCircle,
  failed: AlertCircle,
}

const statusColors = {
  draft: 'text-gray-500',
  mapping: 'text-blue-500',
  ready: 'text-green-500',
  executing: 'text-yellow-500',
  completed: 'text-green-600',
  failed: 'text-red-500',
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.list,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg">
        Failed to load projects. Please try again.
      </div>
    )
  }

  const projects = data?.projects || []

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Migration Projects
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your data migration projects
          </p>
        </div>
        <Link
          to="/projects/new"
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <FolderPlus className="w-5 h-5 mr-2" />
          New Project
        </Link>
      </div>

      {/* Projects list */}
      {projects.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <FolderPlus className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No projects yet
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Create your first migration project to get started
          </p>
          <Link
            to="/projects/new"
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <FolderPlus className="w-5 h-5 mr-2" />
            Create Project
          </Link>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm divide-y divide-gray-200 dark:divide-gray-700">
          {projects.map((project) => {
            const StatusIcon = statusIcons[project.status]
            const statusColor = statusColors[project.status]
            
            return (
              <Link
                key={project.id}
                to={`/projects/${project.id}`}
                className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {project.name}
                    </h3>
                    <span
                      className={`flex items-center text-sm ${statusColor}`}
                    >
                      <StatusIcon className="w-4 h-4 mr-1" />
                      {project.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {project.source_system} → {project.target_system}
                  </p>
                  {project.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1 line-clamp-1">
                      {project.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-4 ml-4">
                  <div className="text-right text-sm text-gray-500 dark:text-gray-400">
                    <div>Created {new Date(project.created_at).toLocaleDateString()}</div>
                    <div>Updated {new Date(project.updated_at).toLocaleDateString()}</div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
