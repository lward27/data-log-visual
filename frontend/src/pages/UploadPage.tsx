import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import type { UploadDetail } from '../lib/types'

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!file) {
      setError('Choose a CSV file first.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      const created = await api.postForm<UploadDetail>('/uploads', formData)
      navigate(`/logs/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-grid">
      <section className="panel upload-panel">
        <div>
          <p className="eyebrow">Upload</p>
          <h2>Bring in a COBB CSV export</h2>
          <p className="muted-copy">
            The backend retains the original file, parses the time axis, indexes all available
            metrics, and builds a chart-ready payload.
          </p>
        </div>

        <form className="stack-form" onSubmit={handleUpload}>
          <label className="file-drop">
            <span>{file ? file.name : 'Choose datalog CSV'}</span>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
          </label>

          {error && <p className="error-text">{error}</p>}

          <button type="submit" className="primary-button" disabled={loading}>
            {loading ? 'Uploading...' : 'Upload and visualize'}
          </button>
        </form>
      </section>

      <section className="panel">
        <p className="eyebrow">What happens next</p>
        <ul className="plain-list">
          <li>We preserve the original CSV on disk for later download.</li>
          <li>We decode COBB exports with a `latin-1` fallback for Windows-style headers.</li>
          <li>We derive metric keys from the CSV columns instead of hardcoding a tiny list.</li>
        </ul>
      </section>
    </div>
  )
}
