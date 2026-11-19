{{- define "sec.env" -}}
envFrom:
  - secretRef:
      name: {{ .Values.secretName }}
env:
{{- range $k, $v := .Values.env }}
  - name: {{ $k }}
    value: {{ $v | quote }}
{{- end }}
{{- end -}}
