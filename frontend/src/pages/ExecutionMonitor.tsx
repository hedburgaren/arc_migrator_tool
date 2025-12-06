import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { executionApi } from '../services/api'
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  Clock,
  Loader,
  Download,
  FileText,
} from 'lucide-react'

const statusConfig = {
  pending: { icon: Clock, color: 'text-gray-500', bg: 'bg-gray-100' },
  running: { icon: Loader, color: 'text-blue-500', bg: 'bg-blue-100' },
  completed: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-100' },
  failed: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-100' },
  cancelled: { icon: XCircle, color: 'text-gray-500', bg: 'bg-gray-100' },
}

const logLevelConfig = {
  debug: { color: 'text-gray-500', bg: 'bg-gray-100' },
  info: { color: 'text-blue-600', bg: 'bg-blue-100' },
  warning: { color: 'text-yellow-600', bg: 'bg-yellow-100' },
  error: { color: 'text-red-600', bg: 'bg-red-100' },
}

export default function ExecutionMonitor() {
  const { projectId, executionId } = useParams<{ projectId: string; executionId: string }>()
  const projectIdNum = parseInt(projectId || '0')
  const executionIdNum = parseInt(executionId || '0')

  const { data: execution, isLoading } = useQuery({
    queryKey: ['execution', executionIdNum],
    queryFn: () => executionApi.get(executionIdNum),
    enabled: !!executionIdNum,
    refetchInterval: (query) => {
      // Poll while running
      const status = query.state.data?.status
      return status === 'running' || status === 'pending' ? 2000 : false
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    )
  }

  if (!execution) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Execution not found</p>
        <Link
          to={`/projects/${projectIdNum}`}
          className="text-primary-600 hover:underline mt-2 inline-block"
        >
          Return to Project
        </Link>
      </div>
    )
  }

  const StatusIcon = statusConfig[execution.status].icon

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link
          to={`/projects/${projectIdNum}`}
          className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Project
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Execution #{execution.id}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Mode: {execution.mode}
            </p>
          </div>
          <span
            className={`flex items-center px-4 py-2 rounded-full text-sm font-medium ${
              statusConfig[execution.status].bg
            } ${statusConfig[execution.status].color}`}
          >
            <StatusIcon
              className={`w-5 h-5 mr-2 ${
                execution.status === 'running' ? 'animate-spin' : ''
              }`}
            />
            {execution.status.charAt(0).toUpperCase() + execution.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <p className="text-sm text-gray-600 dark:text-gray-400">Total Records</p>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white">
            {execution.total_records ?? '-'}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <p className="text-sm text-gray-600 dark:text-gray-400">Processed</p>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white">
            {execution.processed_records}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <p className="text-sm text-gray-600 dark:text-gray-400">Successful</p>
          <p className="text-2xl font-semibold text-green-600">
            {execution.successful_records}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
          <p className="text-2xl font-semibold text-red-600">
            {execution.failed_records}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <p className="text-sm text-gray-600 dark:text-gray-400">Warnings</p>
          <p className="text-2xl font-semibold text-yellow-600">
            {execution.warnings_count}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      {execution.total_records && execution.total_records > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">Progress</span>
            <span className="text-sm font-medium text-gray-900 dark:text-white">
              {Math.round((execution.processed_records / execution.total_records) * 100)}%
            </span>
          </div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                execution.status === 'failed' ? 'bg-red-500' : 'bg-primary-500'
              }`}
              style={{
                width: `${(execution.processed_records / execution.total_records) * 100}%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Output files */}
      {execution.output_files && execution.output_files.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm mb-6">
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <h2 className="font-semibold text-gray-900 dark:text-white">
              Output Files
            </h2>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {execution.output_files.map((file, idx) => (
              <div
                key={idx}
                className="px-4 py-3 flex items-center justify-between"
              >
                <div className="flex items-center">
                  <FileText className="w-5 h-5 text-gray-400 mr-3" />
                  <span className="text-gray-900 dark:text-white">{file}</span>
                </div>
                <button className="flex items-center text-primary-600 hover:text-primary-700">
                  <Download className="w-4 h-4 mr-1" />
                  Download
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error message */}
      {execution.error_message && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <XCircle className="w-5 h-5 text-red-500 mr-2" />
            <h3 className="font-semibold text-red-700 dark:text-red-400">Error</h3>
          </div>
          <p className="mt-2 text-red-600 dark:text-red-300">
            {execution.error_message}
          </p>
        </div>
      )}

      {/* Logs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-semibold text-gray-900 dark:text-white">
            Execution Logs
          </h2>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
          {execution.logs && execution.logs.length > 0 ? (
            execution.logs.map((log) => (
              <div key={log.id} className="px-4 py-2 text-sm">
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${
                      logLevelConfig[log.level].bg
                    } ${logLevelConfig[log.level].color}`}
                  >
                    {log.level.toUpperCase()}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400 text-xs">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  {log.record_index !== null && (
                    <span className="text-gray-500 dark:text-gray-400 text-xs">
                      Row {log.record_index}
                    </span>
                  )}
                </div>
                <p className="mt-1 text-gray-900 dark:text-white">{log.message}</p>
              </div>
            ))
          ) : (
            <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
              No logs available
            </div>
          )}
        </div>
      </div>

      {/* Timestamps */}
      <div className="mt-6 text-sm text-gray-500 dark:text-gray-400">
        <p>Created: {new Date(execution.created_at).toLocaleString()}</p>
        {execution.started_at && (
          <p>Started: {new Date(execution.started_at).toLocaleString()}</p>
        )}
        {execution.completed_at && (
          <p>Completed: {new Date(execution.completed_at).toLocaleString()}</p>
        )}
      </div>
    </div>
  )
}
