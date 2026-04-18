import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { MultiMetricChart } from '../components/MultiMetricChart'
import { api } from '../lib/api'
import type { UploadMetricDetail, UploadVisualization } from '../lib/types'

const preferredMetricKeys = ['rpm', 'boost', 'vehicle-speed', 'feedback-knock']

export function LogDetailPage() {
  const { uploadId } = useParams()
  const [payload, setPayload] = useState<UploadVisualization | null>(null)
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!uploadId) {
      return
    }

    api
      .get<UploadVisualization>(`/uploads/${uploadId}/visualization`)
      .then((data) => {
        setPayload(data)
        const defaults = preferredMetricKeys.filter((key) =>
          data.metrics.some((metric) => metric.key === key),
        )
        setSelectedMetrics(defaults.length ? defaults : data.metrics.slice(0, 4).map((metric) => metric.key))
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load visualization.'))
      .finally(() => setLoading(false))
  }, [uploadId])

  function toggleMetric(key: string) {
    setSelectedMetrics((current) =>
      current.includes(key) ? current.filter((item) => item !== key) : [...current, key],
    )
  }

  const chartMetrics: UploadMetricDetail[] =
    payload?.metrics.filter((metric) => selectedMetrics.includes(metric.key)) || []

  if (loading) {
    return (
      <div className="panel">
        <p className="muted-copy">Loading datalog visualization...</p>
      </div>
    )
  }

  if (error || !payload) {
    return (
      <div className="panel">
        <p className="error-text">{error || 'Datalog not found.'}</p>
      </div>
    )
  }

  const highlights = (payload.summary.highlights as Record<
    string,
    { display_name: string; unit?: string; min_value?: number | null; max_value?: number | null }
  >) || {}

  return (
    <div className="page-grid">
      <section className="panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Visualization</p>
            <h2>{payload.original_filename}</h2>
            <p className="muted-copy">
              {payload.sample_count.toLocaleString()} samples · {payload.available_metrics.length} metrics ·{' '}
              {payload.vehicle_profile || payload.device_label || 'COBB Access Port'}
            </p>
            {payload.map_name && <p className="upload-subtitle">{payload.map_name}</p>}
          </div>
          <a
            className="ghost-button inline-button"
            href={`/api/uploads/${payload.id}/download`}
            target="_blank"
            rel="noreferrer"
          >
            Download original CSV
          </a>
        </div>

        <div className="chart-layout">
          <aside className="metric-picker">
            <p className="eyebrow">Metrics</p>
            <div className="metric-list">
              {payload.available_metrics.map((metric) => (
                <label key={metric.key} className="metric-option">
                  <input
                    type="checkbox"
                    checked={selectedMetrics.includes(metric.key)}
                    onChange={() => toggleMetric(metric.key)}
                  />
                  <span>
                    {metric.display_name}
                    {metric.unit ? ` (${metric.unit})` : ''}
                  </span>
                </label>
              ))}
            </div>
          </aside>

          <div className="panel chart-panel">
            <MultiMetricChart timeAxis={payload.time_axis} metrics={chartMetrics} />
          </div>
        </div>
      </section>

      <section className="stats-row">
        <article className="panel stat-card">
          <p className="eyebrow">Duration</p>
          <strong>{payload.duration_seconds?.toFixed(2) || '0.00'} sec</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Device</p>
          <strong>{payload.device_label || 'Unknown'}</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Map</p>
          <strong>{payload.map_name || 'Unknown'}</strong>
        </article>
        <article className="panel stat-card">
          <p className="eyebrow">Uploaded</p>
          <strong>{new Date(payload.uploaded_at).toLocaleDateString()}</strong>
        </article>
      </section>

      <section className="highlight-grid">
        {Object.entries(highlights).map(([key, value]) => (
          <article key={key} className="panel stat-card">
            <p className="eyebrow">{value.display_name}</p>
            <strong>
              {value.max_value?.toFixed(2) || 'n/a'}
              {value.unit ? ` ${value.unit}` : ''}
            </strong>
            <span className="muted-copy">
              min {value.min_value?.toFixed(2) || 'n/a'}
              {value.unit ? ` ${value.unit}` : ''}
            </span>
          </article>
        ))}
      </section>
    </div>
  )
}
