{{- /*
Erweitere den Chart-Namen, falls nötig.
*/}}
{{- define "seaweedfs-instance.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- /*
Erzeuge einen vollqualifizierten Namen für die Ressourcen.
*/}}
{{- define "seaweedfs-instance.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- /*
Chart-Version und Name als Label.
*/}}
{{- define "seaweedfs-instance.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- /*
Gemeinsame Labels für alle Ressourcen (wichtig für `helm list` und Selektion).
*/}}
{{- define "seaweedfs-instance.labels" -}}
helm.sh/chart: {{ include "seaweedfs-instance.chart" . }}
{{ include "seaweedfs-instance.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- /*
Selector-Labels – werden für die Auswahl von Pods etc. verwendet.
*/}}
{{- define "seaweedfs-instance.selectorLabels" -}}
app.kubernetes.io/name: {{ include "seaweedfs-instance.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- /*
Erzeugt einen Namen für die verwendete ServiceAccount (falls benötigt).
*/}}
{{- define "seaweedfs-instance.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "seaweedfs-instance.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
