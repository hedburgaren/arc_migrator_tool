import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { projectApi } from '../services/api'
import { ArrowLeft, ArrowRight, Check } from 'lucide-react'

const systemOptions = [
  { id: 'csv', name: 'CSV/Excel Files', description: 'Import from CSV or Excel files' },
  { id: 'zoho', name: 'Zoho CRM/Books', description: 'Connect to Zoho CRM or Zoho Books' },
  { id: 'odoo', name: 'Odoo', description: 'Connect to Odoo ERP' },
  { id: 'hubspot', name: 'HubSpot', description: 'Connect to HubSpot CRM' },
  { id: 'shopify', name: 'Shopify', description: 'Connect to Shopify store' },
  { id: 'woocommerce', name: 'WooCommerce', description: 'Connect to WooCommerce store' },
]

export default function ProjectWizard() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    source_system: '',
    target_system: '',
  })

  const createMutation = useMutation({
    mutationFn: projectApi.create,
    onSuccess: (project) => {
      navigate(`/projects/${project.id}`)
    },
  })

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const handleSubmit = () => {
    createMutation.mutate(formData)
  }

  const canProceed = () => {
    if (step === 1) return formData.source_system !== ''
    if (step === 2) return formData.target_system !== ''
    if (step === 3) return formData.name.trim() !== ''
    return false
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Create New Project
        </h1>
      </div>

      {/* Progress steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${
                  s < step
                    ? 'bg-primary-600 text-white'
                    : s === step
                    ? 'bg-primary-100 text-primary-700 border-2 border-primary-600'
                    : 'bg-gray-100 text-gray-500 dark:bg-gray-700'
                }`}
              >
                {s < step ? <Check className="w-5 h-5" /> : s}
              </div>
              {s < 3 && (
                <div
                  className={`w-32 h-1 mx-2 ${
                    s < step ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2 text-sm">
          <span className="text-gray-600 dark:text-gray-400">Source System</span>
          <span className="text-gray-600 dark:text-gray-400">Target System</span>
          <span className="text-gray-600 dark:text-gray-400">Project Details</span>
        </div>
      </div>

      {/* Step content */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        {step === 1 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Select Source System
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Where is your data coming from?
            </p>
            <div className="grid grid-cols-2 gap-4">
              {systemOptions.map((system) => (
                <button
                  key={system.id}
                  onClick={() =>
                    setFormData({ ...formData, source_system: system.id })
                  }
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    formData.source_system === system.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {system.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {system.description}
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Select Target System
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Where should the data go?
            </p>
            <div className="grid grid-cols-2 gap-4">
              {systemOptions.map((system) => (
                <button
                  key={system.id}
                  onClick={() =>
                    setFormData({ ...formData, target_system: system.id })
                  }
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    formData.target_system === system.id
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {system.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {system.description}
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 3 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Project Details
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Give your migration project a name and description
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="e.g., Zoho to Odoo Migration"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Describe the purpose of this migration..."
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                  Summary
                </h3>
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  <p>
                    <span className="font-medium">Source:</span>{' '}
                    {systemOptions.find((s) => s.id === formData.source_system)?.name}
                  </p>
                  <p>
                    <span className="font-medium">Target:</span>{' '}
                    {systemOptions.find((s) => s.id === formData.target_system)?.name}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error message */}
        {createMutation.error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-lg text-sm">
            Failed to create project. Please try again.
          </div>
        )}

        {/* Navigation buttons */}
        <div className="flex justify-between mt-8">
          <button
            onClick={handleBack}
            disabled={step === 1}
            className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
              step === 1
                ? 'text-gray-400 cursor-not-allowed'
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
            }`}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </button>
          {step < 3 ? (
            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                canProceed()
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!canProceed() || createMutation.isPending}
              className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
                canProceed() && !createMutation.isPending
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              }`}
            >
              {createMutation.isPending ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Creating...
                </>
              ) : (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  Create Project
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
