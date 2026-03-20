{{/*
Validiert, dass certificateSource einen erlaubten Wert hat.
Aufruf: {{ include "openshift-ingressoperatorpatch.validateCertificateSource" . }}
*/}}
{{- define "openshift-ingressoperatorpatch.validateCertificateSource" -}}
{{- $validSources := list "cert-manager" "external-secrets" -}}
{{- if not (has .Values.certificateSource $validSources) -}}
{{- fail (printf "Ungültiger Wert für certificateSource: %q. Erlaubte Werte: %s"
      .Values.certificateSource
      (join ", " $validSources)) -}}
{{- end -}}
{{/*
Wenn external-secrets gewählt, prüfen ob secretStoreRef.name gesetzt ist.
*/}}
{{- if eq .Values.certificateSource "external-secrets" -}}
  {{- if not .Values.externalSecrets.secretStoreRef.name -}}
    {{- fail "externalSecrets.secretStoreRef.name muss gesetzt sein wenn certificateSource=external-secrets" -}}
  {{- end -}}
{{/*
Warnung wenn dns_names gesetzt aber data leer – kein ExternalSecret würde erzeugt.
*/}}
  {{- if and .Values.default_ingress_dns_names (not .Values.externalSecrets.ingress.data) -}}
    {{- fail "externalSecrets.ingress.data ist leer, obwohl default_ingress_dns_names gesetzt ist" -}}
  {{- end -}}
  {{- if and .Values.default_api_dns_names (not .Values.externalSecrets.api.data) -}}
    {{- fail "externalSecrets.api.data ist leer, obwohl default_api_dns_names gesetzt ist" -}}
  {{- end -}}
{{- end -}}
{{/*
Wenn cert-manager gewählt, prüfen ob issuerRef gesetzt ist.
*/}}
{{- if eq .Values.certificateSource "cert-manager" -}}
  {{- if not .Values.certManager.issuerRef -}}
    {{- fail "certManager.issuerRef muss gesetzt sein wenn certificateSource=cert-manager" -}}
  {{- end -}}
{{- end -}}
{{- end -}}
{{- define "eso.dataEntries" -}}
{{- range . }}
- secretKey: {{ .secretKey }}
  remoteRef:
    key: {{ .remoteRef.key }}
    property: {{ .remoteRef.property }}
    conversionStrategy: {{ .remoteRef.conversionStrategy | default "Default" }}
    decodingStrategy: {{ .remoteRef.decodingStrategy | default "None" }}
    metadataPolicy: {{ .remoteRef.metadataPolicy | default "None" }}
{{- end }}
{{- end }}
