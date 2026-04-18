import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import type { AuthUser, UploadListItem } from '../lib/types'

export function ProfilePage() {
  const { user, refresh } = useAuth()
  const [displayName, setDisplayName] = useState(user?.display_name || '')
  const [uploads, setUploads] = useState<UploadListItem[]>([])
  const [loadingUploads, setLoadingUploads] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    setDisplayName(user?.display_name || '')
  }, [user?.display_name])

  useEffect(() => {
    api
      .get<UploadListItem[]>('/uploads')
      .then(setUploads)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load account details.'))
      .finally(() => setLoadingUploads(false))
  }, [])

  const stats = useMemo(() => {
    const totalSamples = uploads.reduce((sum, upload) => sum + upload.sample_count, 0)
    const maps = new Set(uploads.map((upload) => upload.map_name).filter(Boolean))
    return {
      totalLogs: uploads.length,
      totalSamples,
      mapsTouched: maps.size,
      lastUpload: uploads[0]?.uploaded_at || null,
    }
  }, [uploads])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      await api.patch<AuthUser>('/auth/me', {
        display_name: displayName,
      })
      await refresh()
      setSuccess('Profile updated.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-grid">
      <section className="panel hero-panel">
        <div>
          <p className="eyebrow">Account</p>
          <h2>Keep your profile ready for the next troubleshooting session.</h2>
          <p className="muted-copy">
            This is the lightweight account layer for MVP: one profile, many uploads, and a clean
            place to confirm what data you already have stored.
          </p>
        </div>
      </section>

      <section className="stats-row">
        <article className="panel stat-card">
          <p className="eyebrow">Stored logs</p>
          <strong>{stats.totalLogs}</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Tracked samples</p>
          <strong>{stats.totalSamples.toLocaleString()}</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Maps touched</p>
          <strong>{stats.mapsTouched}</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Last upload</p>
          <strong>{stats.lastUpload ? new Date(stats.lastUpload).toLocaleDateString() : 'No uploads yet'}</strong>
        </article>
      </section>

      <section className="profile-layout">
        <article className="panel">
          <p className="eyebrow">Profile details</p>
          <form className="stack-form" onSubmit={handleSubmit}>
            <label>
              Display name
              <input
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                maxLength={80}
                placeholder="Driver name"
              />
            </label>

            <label>
              Email
              <input value={user?.email || ''} readOnly disabled />
            </label>

            <label>
              Joined
              <input
                value={user?.created_at ? new Date(user.created_at).toLocaleString() : ''}
                readOnly
                disabled
              />
            </label>

            {error && <p className="error-text">{error}</p>}
            {success && <p className="success-text">{success}</p>}

            <button type="submit" className="primary-button" disabled={saving}>
              {saving ? 'Saving...' : 'Save profile'}
            </button>
          </form>
        </article>

        <article className="panel">
          <div className="section-header">
            <div>
              <p className="eyebrow">Recent uploads</p>
              <h2>Quick account context</h2>
            </div>
          </div>

          {loadingUploads && <p className="muted-copy">Loading upload history...</p>}
          {!loadingUploads && uploads.length === 0 && (
            <p className="muted-copy">No uploads yet. Your future logs will show up here.</p>
          )}
          {!loadingUploads && uploads.length > 0 && (
            <div className="upload-list compact-upload-list">
              {uploads.slice(0, 5).map((upload) => (
                <div key={upload.id} className="upload-card">
                  <div>
                    <p className="upload-title">{upload.original_filename}</p>
                    <p className="muted-copy">
                      {upload.map_name || upload.vehicle_profile || upload.device_label || 'COBB export'}
                    </p>
                  </div>
                  <div className="upload-meta">
                    <span>{new Date(upload.uploaded_at).toLocaleDateString()}</span>
                    <span>{upload.sample_count.toLocaleString()} samples</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </div>
  )
}
