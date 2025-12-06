import { useState, useEffect } from 'react'
import './App.css'
import FileUpload from './components/FileUpload'
import FileList from './components/FileList'
import ProjectManager from './components/ProjectManager'
import { listFiles } from './services/api'
import { FileMetadata } from './types/file'

function App() {
  const [files, setFiles] = useState<FileMetadata[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')

  const loadFiles = async () => {
    try {
      setLoading(true)
      setError('')
      const fileList = await listFiles()
      setFiles(fileList)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFiles()
  }, [])

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>ARC Migrator Tool</h1>
        <p className="subtitle">Data migration made simple</p>
      </header>
      <main className="app-main">
        <div className="content-wrapper">
          <section className="upload-section">
            <h2 className="section-title">Upload Files</h2>
            <FileUpload onUploadSuccess={loadFiles} />
          </section>

          <section className="files-section">
            {loading && (
              <div className="loading-message">Loading files...</div>
            )}
            {error && (
              <div className="error-message">{error}</div>
            )}
            {!loading && !error && (
              <FileList files={files} onFileDeleted={loadFiles} />
            )}
          </section>

          <section className="projects-section">
            {!loading && !error && (
              <ProjectManager files={files} />
            )}
          </section>
        </div>
      </main>
      <footer className="app-footer">
        <p>Version 0.1.0 | ARC Migrator Tool</p>
      </footer>
    </div>
  )
}

export default App
