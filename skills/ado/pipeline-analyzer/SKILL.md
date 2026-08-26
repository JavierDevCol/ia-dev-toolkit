---
name: ado-pipeline-analyzer
description: >
  Usa esta skill cuando necesites analizar un build o pipeline de Azure DevOps.
  Sirve al revisar por qué falló un build, inspeccionar logs de pipeline, ver el
  estado de una ejecución, revisar cambios incluidos en un build, Stages
  (approvals, gates, deployment jobs), o cuando te pidan "analizar build",
  "revisar pipeline", "ver logs del pipeline", "qué pasó en el build",
  "build fallido", "check pipeline status", "revisar stage", "ver cambios del
  build", "pipeline run details". Obtiene información del build, logs por etapa,
  cambios asociados, estado de stages y genera un reporte estructurado.
compatibility: Requires Azure DevOps MCP server configured
---

# ADO Pipeline Analyzer

Analiza ejecuciones de pipeline en Azure DevOps y genera reporte con hallazgos.

## Contexto del perfil activo

Esta skill recibe del agente orquestador el contexto ya resuelto:
- `project_name` — proyecto ADO resuelto desde `project_map.repos`
- `base_reports_path` — ruta base de reportes

La skill **no lee `config_consultas.json` directamente**. Todo el contexto es inyectado por el agente.

Si el contexto no fue pasado, solicita al usuario que re-invoque desde el agente principal.

## Fase A — Identificar el build y alcance del análisis

Preguntar al usuario si no se proporcionó explícitamente:

1. **Pipeline** — nombre o ID del pipeline
2. **Build** — número de build, ID de ejecución, o "última ejecución"
3. **Rama** (opcional) — filtrar por rama si aplica

Luego preguntar:

> ¿Quieres un análisis **general** de todo el build o de algún **stage/job específico**?

| Opción | Qué incluye |
|--------|-------------|
| **General** | Estado general, cambios, todos los stages, resumen de errores/warnings |
| **Stage/job específico** | Detalle de un stage/job en particular, sus tareas, logs de esa etapa |

Si el usuario elige **específico**, preguntar qué stage/job (o permitir elegir de la lista una vez obtenidos los stages).

Si el usuario proporciona un link de ADO, extraer project/pipeline/build desde la URL.

## Fase B — Obtener datos del build

Usar las tools de ADO según corresponda:

### B1 — Buscar el pipeline

```bash
# Listar pipelines disponibles si no se conoce el nombre
ado/pipelines_get_build_definitions --project "$project_name"
```

Extraer `definitionId` del pipeline a analizar.

### B2 — Obtener la ejecución del build

```bash
# Listar ejecuciones recientes si no se dio un build específico
ado/pipelines_list_runs --project "$project_name" --pipeline-id "$definitionId" --top 5

# Obtener run específico si se conoce el runId
ado/pipelines_get_run --project "$project_name" --pipeline-id "$definitionId" --run-id "$runId"
```

Extraer del resultado:
- `id` (runId)
- `state` (inProgress, completed, canceled, failed)
- `result` (succeeded, failed, canceled)
- `createdDate`, `finishedDate`
- `triggerInfo` (commit, PR)
- `resources.repositories.self.version` (commit/ref)

### B3 — Obtener cambios del build

```bash
ado/pipelines_get_build_changes --project "$project_name" --build-id "$runId"
```

Extraer: commits incluidos, autores, mensajes.

### B4 — Obtener logs y estado de stages

```bash
# Obtener información del timeline/stages
ado/pipelines_get_build_status --project "$project_name" --build-id "$runId"
```

Extraer por cada stage/job/task:
- Nombre
- Estado (pending, running, completed, skipped, failed)
- Resultado (succeeded, failed, succeededWithIssues)
- Errores y warnings
- Start/finish time

### B5 — Obtener logs detallados (opcional, bajo demanda)

```bash
# Log completo del build
ado/pipelines_get_build_log --project "$project_name" --build-id "$runId"

# Log por ID específico
ado/pipelines_get_build_log_by_id --project "$project_name" --build-id "$runId" --log-id "$logId"
```

Solo si el usuario pide revisar logs específicos o hay errores que requieran inspección.

## Fase C — Clasificar hallazgos

Para cada elemento detectado, clasificar:

| Categoría | Ejemplos |
|-----------|----------|
| ❌ Errores | Tareas fallidas, exit codes distintos de 0, excepciones |
| ⚠️ Warnings | Tests fallidos, coverage baja, dependencias obsoletas |
| ℹ️ Info | Cambios incluidos, duración, stages ejecutados |
| ✅ Éxito | Stages completados sin errores |

## Fase D — Generar reporte

Generar `PIPELINE-REPORT_{runId}.md` en `{base_reports_path}/` con la siguiente estructura:

```markdown
# PIPELINE-REPORT_{runId} — {pipeline_name}

> **Build:** #{runId}
> **Estado:** {state} | **Resultado:** {result}
> **Rama:** {branch} | **Commit:** {commitHash}
> **Inicio:** {startTime} | **Fin:** {endTime} | **Duración:** {duration}
> **Trigger:** {triggerType} {triggerDetail}
> **URL:** {buildUrl}

## 1. Resumen

{Resultado general del build}

## 2. Commits incluidos

| Commit | Autor | Mensaje |
|--------|-------|---------|
| {hash} | {author} | {message} |

## 3. Stages / Jobs

| Stage | Estado | Resultado | Duración | Errores |
|-------|--------|-----------|----------|---------|
| {stageName} | {status} | {result} | {duration} | {errorCount} |

## 4. Hallazgos

### ❌ Errores
{lista de errores detectados}

### ⚠️ Warnings
{lista de warnings}

### ℹ️ Información adicional
{detalles relevantes}

## 5. Recomendaciones

{acciones sugeridas según los hallazgos}
```

## Reglas

1. Siempre preguntar qué build analizar si no se especificó
2. No mostrar logs completos a menos que el usuario los pida explícitamente
3. Si el build tiene stages con approvals/gates pendientes, indicarlo en hallazgos
4. Si hay cambios sin autor aparente, indicar "cambio automático" en lugar de omitir
5. El reporte se guarda en `{base_reports_path}/PIPELINE-REPORT_{runId}.md`

## Gotchas

- **Pipeline ID ≠ Build ID:** El pipeline tiene un `definitionId` fijo. Cada ejecución tiene un `runId` distinto. No confundirlos.
- **Build en progreso:** Si el build aún está corriendo, solo se puede mostrar estado parcial. Indicar al usuario que el reporte es preliminar.
- **Logs truncados:** `ado/pipelines_get_build_log` puede devolver logs truncados si el build es muy grande. Usar `ado/pipelines_get_build_log_by_id` para logs específicos de stage/job.
- **Multi-stage pipelines:** Los stages pueden tener approve gates. Si un stage no se ejecutó, puede ser por gates no aprobados, no por error técnico.
- **Cambios vacíos:** Algunos builds (ej. schedules, triggers automáticos) pueden no tener cambios asociados. Indicar "Sin cambios detectados".
- **Permisos:** Si las tools devuelven 401/403, informar que el perfil no tiene permisos para ver ese pipeline/build.
