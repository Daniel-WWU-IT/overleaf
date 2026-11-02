{{/*
Basic chart helpers
*/}}

{{ define "overleafv6.chart" -}}
{{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{ define "overleafv6.name" -}}
{{ default "overleafv6" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{ define "overleafv6.fullname" -}}
{{ default "overleafv6" .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{ define "overleafv6.namespace" }}
{{ default "" .Values.namespace }}
{{- end}}

{{ define "overleafv6.labels" -}}
helm.sh/chart: {{ include "overleafv6.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{ include "overleafv6.selectorLabels" . }}
{{- end }}

{{ define "overleafv6.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/name: {{ include "overleafv6.name" . }}
{{- end }}
