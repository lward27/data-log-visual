export interface AuthUser {
  id: string
  email: string
  display_name: string | null
  created_at: string
}

export interface UploadMetricSummary {
  key: string
  display_name: string
  unit: string | null
  sample_count: number
  min_value: number | null
  max_value: number | null
  position: number
}

export interface UploadMetricDetail extends UploadMetricSummary {
  values: Array<number | null>
}

export interface UploadListItem {
  id: string
  original_filename: string
  source_format: string
  uploaded_at: string
  file_size_bytes: number
  sample_count: number
  duration_seconds: number | null
  metric_count: number
  device_label: string | null
  vehicle_profile: string | null
}

export interface UploadDetail extends UploadListItem {
  summary: Record<string, unknown>
  source_metadata: Record<string, unknown>
  available_metrics: UploadMetricSummary[]
}

export interface UploadVisualization extends UploadDetail {
  time_axis: number[]
  metrics: UploadMetricDetail[]
}
