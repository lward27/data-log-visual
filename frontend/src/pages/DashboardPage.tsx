import { Link } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import type { UploadListItem } from '../lib/types'

export function DashboardPage() {
  const [uploads, setUploads] = useState<UploadListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'recent' | 'oldest' | 'samples'>('recent')

  useEffect(() => {
    api
      .get<UploadListItem[]>('/uploads')
      .then(setUploads)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load uploads.'))
      .finally(() => setLoading(false))
  }, [])

  const visibleUploads = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase()
    const filtered = normalizedSearch
      ? uploads.filter((upload) =>
          [
            upload.original_filename,
            upload.vehicle_profile,
            upload.device_label,
            upload.map_name,
          ]
            .filter(Boolean)
            .some((value) => value?.toLowerCase().includes(normalizedSearch)),
        )
      : uploads

    return [...filtered].sort((left, right) => {
      if (sortBy === 'oldest') {
        return new Date(left.uploaded_at).getTime() - new Date(right.uploaded_at).getTime()
      }
      if (sortBy === 'samples') {
        return right.sample_count - left.sample_count
      }
      return new Date(right.uploaded_at).getTime() - new Date(left.uploaded_at).getTime()
    })
  }, [searchTerm, sortBy, uploads])

  return (
    <div className="page-grid">
      <section className="panel hero-panel">
        <div>
          <p className="eyebrow">MVP workflow</p>
          <h2>Upload a datalog and go straight to the chart.</h2>
          <p className="muted-copy">
            The current build stores your CSV, parses available metrics dynamically, and keeps a
            library you can reopen later.
          </p>
        </div>
        <Link to="/upload" className="primary-button inline-button">
          Upload new log
        </Link>
      </section>

      <section className="stats-row">
        <article className="panel stat-card">
          <p className="eyebrow">Stored logs</p>
          <strong>{uploads.length}</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Most recent source</p>
          <strong>{uploads[0]?.source_format || 'No uploads yet'}</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Sample coverage</p>
          <strong>
            {uploads.length
              ? `${Math.max(...uploads.map((upload) => upload.sample_count)).toLocaleString()} rows`
              : 'n/a'}
          </strong>
        </article>
      </section>

      <section className="panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Library</p>
            <h2>Your uploaded datalogs</h2>
          </div>
          <div className="toolbar">
            <label className="toolbar-field">
              <span>Search</span>
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Filename, map, device"
              />
            </label>
            <label className="toolbar-field">
              <span>Sort</span>
              <select
                value={sortBy}
                onChange={(event) =>
                  setSortBy(event.target.value as 'recent' | 'oldest' | 'samples')
                }
              >
                <option value="recent">Most recent</option>
                <option value="oldest">Oldest</option>
                <option value="samples">Most samples</option>
              </select>
            </label>
          </div>
        </div>

        {loading && <p className="muted-copy">Loading uploads...</p>}
        {!loading && error && <p className="error-text">{error}</p>}
        {!loading && !error && uploads.length === 0 && (
          <div className="empty-state">
            <h3>No datalogs yet</h3>
            <p>Start with one of the COBB CSV exports and we’ll build the metric index for you.</p>
          </div>
        )}
        {!loading && !error && uploads.length > 0 && visibleUploads.length === 0 && (
          <div className="empty-state">
            <h3>No matches</h3>
            <p>Try a different filename, map name, or device search.</p>
          </div>
        )}

        <div className="upload-list">
          {visibleUploads.map((upload) => (
            <Link key={upload.id} to={`/logs/${upload.id}`} className="upload-card">
              <div>
                <p className="upload-title">{upload.original_filename}</p>
                <p className="muted-copy">
                  {new Date(upload.uploaded_at).toLocaleString()} · {upload.sample_count.toLocaleString()} samples
                </p>
                {upload.map_name && <p className="upload-subtitle">{upload.map_name}</p>}
              </div>
              <div className="upload-meta">
                <span>{upload.metric_count} metrics</span>
                <span>{upload.vehicle_profile || upload.device_label || 'COBB export'}</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
