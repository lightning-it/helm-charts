{{- define "openshift-ingressoperatorpatch.validateCertificateSource" -}}
{{- $validSources := list "cert-manager" "external-secrets" -}}
{{- if not (has .Values.certificateSource $validSources) -}}
{{- fail (printf "Ungültiger Wert für certificateSource: %q. Erlaubte Werte: %s"
      .Values.certificateSource
      (join ", " $validSources)) -}}
{{- end -}}
{{- if eq .Values.certificateSource "external-secrets" -}}
  {{- if not .Values.externalSecrets.secretStoreRef.name -}}
    {{- fail "externalSecrets.secretStoreRef.name muss gesetzt sein wenn certificateSource=external-secrets" -}}
  {{- end -}}
  {{- if and .Values.ingress.enabled (not .Values.externalSecrets.ingress.data) -}}
    {{- fail "externalSecrets.ingress.data ist leer, obwohl ingress.enabled=true" -}}
  {{- end -}}
  {{- if and .Values.api.enabled (not .Values.externalSecrets.api.data) -}}
    {{- fail "externalSecrets.api.data ist leer, obwohl api.enabled=true" -}}
  {{- end -}}
{{- end -}}
{{- if eq .Values.certificateSource "cert-manager" -}}
  {{- if not .Values.certManager.issuerRef -}}
    {{- fail "certManager.issuerRef muss gesetzt sein wenn certificateSource=cert-manager" -}}
  {{- end -}}
  {{- if and .Values.ingress.enabled (not .Values.ingress.dnsNames) -}}
    {{- fail "ingress.dnsNames muss gesetzt sein wenn ingress.enabled=true" -}}
  {{- end -}}
  {{- if and .Values.api.enabled (not .Values.api.dnsNames) -}}
    {{- fail "api.dnsNames muss gesetzt sein wenn api.enabled=true" -}}
  {{- end -}}
{{- end -}}
{{- end -}}

{{- define "openshift-ingressoperatorpatch.eso.dataEntries" -}}
{{- range . }}
- secretKey: {{ .secretKey }}
  remoteRef:
    key: {{ .remoteRef.key }}
    property: {{ .remoteRef.property }}
    conversionStrategy: {{ .remoteRef.conversionStrategy | default "Default" }}
    decodingStrategy: {{ .remoteRef.decodingStrategy | default "None" }}
    metadataPolicy: {{ .remoteRef.metadataPolicy | default "None" }}
{{- end }}
{{- end -}}
