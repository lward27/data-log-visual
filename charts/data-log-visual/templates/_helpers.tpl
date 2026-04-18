{{- define "data-log-visual.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "data-log-visual.frontendName" -}}
{{- printf "%s-frontend" (include "data-log-visual.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "data-log-visual.backendName" -}}
{{- printf "%s-backend" (include "data-log-visual.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
