import { CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'

interface PreviewDashboardProps {
  sourceData: Record<string, unknown>[]
  transformedData: Record<string, unknown>[]
  warnings: Array<{
    type: string
    message: string
    row_index?: number
    target_field?: string
  }>
  warningsCount: number
}

export default function PreviewDashboard({
  sourceData,
  transformedData,
  warnings,
  warningsCount,
}: PreviewDashboardProps) {
  const sourceColumns = sourceData.length > 0 ? Object.keys(sourceData[0]) : []
  const targetColumns = transformedData.length > 0 ? Object.keys(transformedData[0]) : []

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="flex items-center space-x-2">
            <Info className="w-5 h-5 text-blue-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Source Rows</span>
          </div>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white mt-1">
            {sourceData.length}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Transformed</span>
          </div>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white mt-1">
            {transformedData.length}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Warnings</span>
          </div>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white mt-1">
            {warningsCount}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Errors</span>
          </div>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white mt-1">
            0
          </p>
        </div>
      </div>

      {/* Data comparison */}
      <div className="grid grid-cols-2 gap-4">
        {/* Source data */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900/20">
            <h3 className="font-semibold text-gray-900 dark:text-white">Source Data</h3>
          </div>
          <div className="overflow-x-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0">
                <tr>
                  {sourceColumns.map((col) => (
                    <th
                      key={col}
                      className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {sourceData.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    {sourceColumns.map((col) => (
                      <td
                        key={col}
                        className="px-3 py-2 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap"
                      >
                        {String(row[col] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Transformed data */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-green-50 dark:bg-green-900/20">
            <h3 className="font-semibold text-gray-900 dark:text-white">Transformed Data</h3>
          </div>
          <div className="overflow-x-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0">
                <tr>
                  {targetColumns.map((col) => (
                    <th
                      key={col}
                      className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {transformedData.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    {targetColumns.map((col) => (
                      <td
                        key={col}
                        className="px-3 py-2 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap"
                      >
                        {String(row[col] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm">
          <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-yellow-50 dark:bg-yellow-900/20">
            <h3 className="font-semibold text-gray-900 dark:text-white flex items-center">
              <AlertTriangle className="w-5 h-5 text-yellow-500 mr-2" />
              Warnings ({warnings.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-48 overflow-y-auto">
            {warnings.map((warning, idx) => (
              <div key={idx} className="px-4 py-2 text-sm">
                <span className="text-gray-900 dark:text-white">{warning.message}</span>
                {warning.row_index !== undefined && (
                  <span className="text-gray-500 dark:text-gray-400 ml-2">
                    (Row {warning.row_index})
                  </span>
                )}
                {warning.target_field && (
                  <span className="text-gray-500 dark:text-gray-400 ml-2">
                    → {warning.target_field}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
