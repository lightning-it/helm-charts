{{- define "generic-clusterconfig.SecretKey" -}}
{{- if .Values.externalSecrets.secretPath -}}
  {{ .Values.externalSecrets.secretPath | quote }}
{{- else -}}
  {{ printf "%s/%s/%s/%s" (substr 4 7 .Values.envName) (substr 1 4 .Values.envName) .Values.envName .Release.Name }}
{{- end -}}
{{- end }}

{{/*
Expand the name of the chart.
*/}}
{{- define "generic-clusterconfig.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "generic-clusterconfig.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "generic-clusterconfig.labels" -}}
helm.sh/chart: {{ include "generic-clusterconfig.chart" . }}
{{ include "generic-clusterconfig.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.global.labels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "generic-clusterconfig.selectorLabels" -}}
app.kubernetes.io/name: {{ include "generic-clusterconfig.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the namespace name for LDAP sync
*/}}
{{- define "generic-clusterconfig.ldapGroupSync.namespace" -}}
{{- default "openshift-config" .Values.ldapGroupSync.namespace }}
{{- end }}

{{/*
Create the LDAP sync config
*/}}
{{- define "generic-clusterconfig.ldapGroupSync.config" -}}
kind: LDAPSyncConfig
apiVersion: v1
url: {{ .Values.ldapGroupSync.ldap.url | quote }}
bindDN: {{ .Values.ldapGroupSync.ldap.bindDN | quote }}
bindPassword:
  file: {{ printf "/etc/secrets/%s" .Values.ldapGroupSync.secrets.bindPassword.fileName | quote }}
insecure: false
ca: {{ printf "/etc/ipa-ca/%s" .Values.ldapGroupSync.secrets.caCert.fileName | quote }}
rfc2307:
  groupsQuery:
    baseDN: {{ .Values.ldapGroupSync.ldap.groups.baseDN | quote }}
    scope: sub
    derefAliases: never
    filter: {{ .Values.ldapGroupSync.ldap.groups.filter | quote }}
    pageSize: 0
  groupUIDAttribute: {{ .Values.ldapGroupSync.ldap.groupUIDAttribute | quote }}
  groupNameAttributes:
  {{- range .Values.ldapGroupSync.ldap.groupNameAttributes }}
  - {{ . | quote }}
  {{- end }}
  groupMembershipAttributes:
  {{- range .Values.ldapGroupSync.ldap.groupMembershipAttributes }}
  - {{ . | quote }}
  {{- end }}
  usersQuery:
    baseDN: {{ .Values.ldapGroupSync.ldap.users.baseDN | quote }}
    scope: sub
    derefAliases: never
    pageSize: 0
  userUIDAttribute: {{ .Values.ldapGroupSync.ldap.userUIDAttribute | quote }}
  userNameAttributes:
  {{- range .Values.ldapGroupSync.ldap.userNameAttributes }}
  - {{ . | quote }}
  {{- end }}
  tolerateMemberNotFoundErrors: {{ .Values.ldapGroupSync.ldap.tolerateMemberNotFoundErrors }}
  tolerateMemberOutOfScopeErrors: {{ .Values.ldapGroupSync.ldap.tolerateMemberOutOfScopeErrors }}
{{- end }}

{{/*
Generate safe name for cluster role bindings
*/}}
{{- define "generic-clusterconfig.ldapGroupSync.safeName" -}}
{{- $name := . | replace "." "-" | replace "_" "-" | replace ":" "-" | lower -}}
{{- printf "ldap-%s" $name -}}
{{- end -}}

{{/*
Generate cluster role binding name
*/}}
{{- define "generic-clusterconfig.ldapGroupSync.crbName" -}}
{{- $group := .group | default "" -}}
{{- $role := .role | default "" -}}
{{- $namespace := .namespace | default "" -}}
{{- $suffix := "" -}}
{{- if $namespace -}}
  {{- $suffix = printf "-%s" ($namespace | replace "." "-" | replace "_" "-" | lower) -}}
{{- end -}}
{{- printf "%s-%s%s" (include "generic-clusterconfig.ldapGroupSync.safeName" $group) (include "generic-clusterconfig.ldapGroupSync.safeName" $role) $suffix -}}
{{- end -}}

{{/*
Get the root context for label generation
*/}}
{{- define "generic-clusterconfig.root" -}}
{{- if .Values -}}
{{- . -}}
{{- else -}}
{{- $root := index . 0 -}}
{{- $root -}}
{{- end -}}
{{- end -}}
