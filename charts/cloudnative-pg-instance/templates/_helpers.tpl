{{- define "cloudnative-pg-instance.SecretKey" -}}
{{- if .Values.externalSecrets.secretPath -}}
  {{ .Values.externalSecrets.secretPath | quote }}
{{- else -}}
  {{ printf "%s/%s/%s/%s" (substr 1 4 .Values.envName) (substr 4 7 .Values.envName) .Values.envName .Release.Name }}
{{- end -}}
{{- end }}
