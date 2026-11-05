# Pipeline Report Template

Report file: `{base_reports_path}/PIPELINE-REPORT_{runId}.md`

```markdown
# PIPELINE-REPORT_{runId} — {pipeline_name}

> **Build:** #{runId}
> **Status:** {state} | **Result:** {result}
> **Branch:** {branch} | **Commit:** {commitHash}
> **Started:** {startTime} | **Finished:** {endTime} | **Duration:** {duration}
> **Trigger:** {triggerType} {triggerDetail}
> **URL:** {buildUrl}

## 1. Summary

{Overall build result}

## 2. Included Commits

| Commit | Author | Message |
|--------|--------|---------|
| {hash} | {author} | {message} |

## 3. Stages / Jobs (executed)

| Stage | Status | Result | Duration | Errors |
|-------|--------|--------|----------|--------|
| {stageName} | {status} | {result} | {duration} | {errorCount} |

## 4. Run Integrity

> **Cancelation check:** {natural end — `finishedDate` + `Set build status` / canceled — evidence}
> **Stage coverage:** {N de M stages ejecutados; cuáles se omitieron y por qué condición}

| Stage declared | Executed | Condition | Evidence |
|----------------|----------|-----------|----------|
| {stageName} | yes/no | {condition or —} | {log `##[section]Starting: ...` or "no logs"} |

## 5. Findings

### Errors
{detected errors}

### Warnings
{detected warnings}

### Information
{relevant details}

## 6. Recommendations

{suggested actions based on findings}

> **Analista:** Pipeline Analyzer - {{usuario.nombre}}
> **Fecha:** {fecha}
```

Si `usuario.nombre` no está configurado (o `usuario.incluir_firma_en_documentos` es `false`), la línea queda `> **Analista:** Pipeline Analyzer` (sin el sufijo) u omitir la línea por completo.
