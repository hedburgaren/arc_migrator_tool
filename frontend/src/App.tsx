import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ProjectWizard from './pages/ProjectWizard'
import ProjectDetail from './pages/ProjectDetail'
import MappingWorkspace from './pages/MappingWorkspace'
import ExecutionMonitor from './pages/ExecutionMonitor'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects/new" element={<ProjectWizard />} />
        <Route path="/projects/:projectId" element={<ProjectDetail />} />
        <Route path="/projects/:projectId/mapping/:profileId" element={<MappingWorkspace />} />
        <Route path="/projects/:projectId/execution/:executionId" element={<ExecutionMonitor />} />
      </Routes>
    </Layout>
  )
}

export default App
