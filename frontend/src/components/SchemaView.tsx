import type { FieldDefinition } from '../types'
import { Database, Key, List, Hash, Calendar, ToggleLeft } from 'lucide-react'

interface SchemaViewProps {
  name: string
  fields: FieldDefinition[]
  onFieldClick?: (field: FieldDefinition) => void
  selectedFieldId?: number
  type?: 'source' | 'target'
}

const fieldTypeIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  string: Hash,
  integer: Hash,
  float: Hash,
  boolean: ToggleLeft,
  date: Calendar,
  datetime: Calendar,
  enum: List,
  lookup: List,
  json: Database,
  unknown: Hash,
}

const fieldTypeColors: Record<string, string> = {
  string: 'text-blue-500',
  integer: 'text-green-500',
  float: 'text-green-500',
  boolean: 'text-purple-500',
  date: 'text-orange-500',
  datetime: 'text-orange-500',
  enum: 'text-pink-500',
  lookup: 'text-pink-500',
  json: 'text-cyan-500',
  unknown: 'text-gray-500',
}

export default function SchemaView({
  name,
  fields,
  onFieldClick,
  selectedFieldId,
  type = 'source',
}: SchemaViewProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div
        className={`px-4 py-3 border-b border-gray-200 dark:border-gray-700 ${
          type === 'source' ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-green-50 dark:bg-green-900/20'
        }`}
      >
        <div className="flex items-center space-x-2">
          <Database
            className={`w-5 h-5 ${
              type === 'source' ? 'text-blue-500' : 'text-green-500'
            }`}
          />
          <h3 className="font-semibold text-gray-900 dark:text-white">{name}</h3>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {fields.length} fields
        </p>
      </div>

      {/* Fields list */}
      <div className="divide-y divide-gray-100 dark:divide-gray-700 max-h-96 overflow-y-auto">
        {fields.map((field) => {
          const Icon = fieldTypeIcons[field.field_type] || Hash
          const colorClass = fieldTypeColors[field.field_type] || 'text-gray-500'
          const isSelected = selectedFieldId === field.id

          return (
            <div
              key={field.id}
              onClick={() => onFieldClick?.(field)}
              className={`px-4 py-2 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                onFieldClick ? 'cursor-pointer' : ''
              } ${isSelected ? 'bg-primary-50 dark:bg-primary-900/30' : ''}`}
            >
              <div className="flex items-center space-x-2">
                <Icon className={`w-4 h-4 ${colorClass}`} />
                <span className="text-sm text-gray-900 dark:text-white">
                  {field.display_name || field.name}
                </span>
                {field.is_primary_key && (
                  <Key className="w-3 h-3 text-yellow-500" />
                )}
                {field.is_required && (
                  <span className="text-red-500 text-xs" title="Required">*</span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {field.is_lookup && (
                  <span className="px-2 py-0.5 text-xs bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-300 rounded">
                    lookup
                  </span>
                )}
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {field.field_type}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
