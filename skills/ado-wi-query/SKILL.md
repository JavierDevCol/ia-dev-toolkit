---
name: ado-wi-query
description: >
  Use when the user wants to see, list, or review their Azure DevOps Work Items:
  "mis WIs", "qué tengo asignado", "mis work items activos", "WIQL", "query
  guardada", or a filtered WI listing by state, type, iteration, parent or dates.
  Read-only consultation. Do not use for creating or updating WIs, comments,
  PRs, pipelines or releases.
ready: true
---

# ADO WI Query

## Overview

Consulta de solo lectura de los Work Items de Azure DevOps del usuario ("mis WIs").
Usuario y proyecto se resuelven desde la config SAC (`ado.config`); la consulta se
ejecuta con las tools MCP del servidor `ado`. Nunca crea ni modifica WIs.

## When to Use

- "¿Qué WIs tengo asignados?", "muéstrame mis work items activos"
- Listados filtrados: por estado, tipo, iteración, padre/hijas o rango de fechas
- Ejecutar la `default_query` (query guardada) del perfil ADO

### Cuándo NO usar

- Comentar, actualizar o reasignar WIs → `ado-wi-comments`
- Crear tareas o publicar HUs → `ado-task-creator` / `ado-hu-publisher`
- PRs, pipelines o releases → `ado-pr-*`, `ado-pipeline-analyzer`, `handoff-release`

## Implementation

### 1. Leer config con memctl (solo lectura; su salida ES la respuesta)

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa
tal cual en el resto de la skill (no recalcular ni inventar valores):

| Placeholder / dato | Valor = salida de |
|---|---|
| `{perfil}` | `sh .SAC/memctl.sh get ado.config.perfil_activo` |
| `{user_email}` | `sh .SAC/memctl.sh get ado.config.perfiles.$P.user_email` (con `P={perfil}`) |
| `{project_wi}` | `sh .SAC/memctl.sh get ado.config.perfiles.$P.project_map.workitems` (fallback: `project_map.default`) |
| `{default_query}` | `sh .SAC/memctl.sh get ado.config.perfiles.$P.default_query` |
| `{ado_org}` | `sh .SAC/memctl.sh get ado.config.perfiles.$P.config_extras.ado_org` (solo si hace falta fallback REST) |

- Exit 0 + `null` → dato no configurado: aplicar los guards de abajo.
- Exit 2 → clave o archivo inexistente: tratarlo como no configurado.
- Exit 127 (memctl no existe) → leer `.SAC/config/sac.json` con `jq`.
- Exit 1 (JSON inválido, truncado o vacío) → detenerse y avisar al usuario: no leer
  ni editar el archivo a mano. Nunca inventar valores.
- Consultar solo las claves de esta skill; no volcar secciones completas.
- Los campos reales del perfil son los de la tabla (más `config_extras`,
  `colaboradores`, `base_reports_path`): **no existen** claves `organizacion` ni
  `proyecto`. Esquema completo: `ado-profile-setup/references/config-schema.md`.

**Profile guard:** si `{perfil}` es `null`/vacío, el perfil no existe o `{project_wi}`
no resuelve → detenerse y responder: "ADO sin configurar: ejecutar `ado-profile-setup`".
No pidas organización, proyecto ni usuario a mano; no improvises un onboarding.

**Campos faltantes:** si el perfil existe pero falta solo `{user_email}` o
`{project_wi}`, preguntar una vez y persistir únicamente esa sub-sección
`ado.config.perfiles.<perfil>` en `.SAC/config/sac.json` (memctl solo lee).

### 2. Elegir la consulta

Aplicar la primera que corresponda:

1. `{default_query}` existe y su `resumen_legible` coincide con lo pedido →
   `tipo: saved_query` ⇒ `wit_get_query_results_by_id` (`query_id`);
   `tipo: wiql` ⇒ `wit_query_by_wiql` (con `query`).
2. "Mis WIs" **sin adjetivos de estado** ("mis WIs", "lo que tengo asignado") →
   `wit_my_work_items`.
3. Cualquier mención de estado ("activos", "abiertos", "sin cerrar", "en curso") o
   cualquier otro filtro (tipo, iteración, padre, fechas) → WIQL con la plantilla.
   Ej.: "mis WIs activos" **es filtro de estado** → esta ruta, no la 2.

```sql
SELECT [System.Id] FROM WorkItems
WHERE [System.TeamProject] = '{project_wi}'
  AND [System.AssignedTo] = @Me
  AND [System.State] IN ('Active', 'New')
ORDER BY [System.ChangedDate] DESC
```

- `@Me` = identidad autenticada. Si no se filtra por usuario, quitar esa cláusula.
- Estados de cierre varían por proceso (EN/ES): "activos" ⇒ `IN ('Active','New')`;
  "todos" ⇒ sin filtro de estado. Si el resultado no cuadra con lo esperado,
  confirmar con el usuario el vocabulario de estados; nunca inventarlo.
- Hijas de unos padres: `AND [System.Parent] IN (<ids>)`. Nunca `expand: Relations`
  (falla por tamaño con HTML largo).

### 3. Ejecutar (MCP primero)

1. Usar las tools del servidor MCP `ado` (cargar con ToolSearch si no están). Usa
   **solo** los nombres de tools listados en la tabla *Quick Reference* de esta
   skill. Si una operación no está cubierta por esos nombres, dilo — **nunca
   inventes nombres de tools ni busques catálogos externos en runtime**.
2. **`project` = `{project_wi}` en TODA llamada** (sin él: `Project selection cancelled.`).
3. Las queries devuelven IDs; el detalle va en un segundo paso:
   `wit_get_work_items_batch_by_ids` con `fields` explícitos:
   `System.WorkItemType`, `System.Title`, `System.State`, `System.AssignedTo`,
   `System.IterationPath`, `System.ChangedDate` (agregar más solo si se piden).
4. Sin servidor MCP `ado` disponible: informar SOLO eso y pedir que se conecte (el
   profile guard y `ado-profile-setup` no aplican aquí: no mezclar los mensajes).
   Fallback REST+PAT solo como último recurso (patrón de `ado-variable-groups`:
   PAT en `.env`, clave `pat_ado`, org = `{ado_org}`; nunca imprimir el PAT).

### 4. Salida

Tabla compacta en español, una fila por WI (máx. 20 por defecto):

> **Tus Work Items en `{project_wi}`:**
>
> | ID | Tipo | Título | Estado | Iteración | Últ. cambio |
> |---|---|---|---|---|---|
> | [12345](https://dev.azure.com/{ado_org}/{project_wi}/_workitems/edit/12345) | User Story | … | Active | Sprint 24 | 2026-10-27 |
>
> **Total: N** (M User Stories · K Bugs · J Tasks)

- 0 resultados → "No tienes work items que cumplan el filtro en `{project_wi}`."
- Si se pide archivo de reporte: escribirlo bajo `base_reports_path` del perfil
  (idioma y formato de fecha según `config_extras`).
- Solo lectura: si el usuario quiere comentar/cambiar algo, derivar al skill que toca.

## Quick Reference

| Operación | Tool | Parámetros clave |
|-----------|------|------------------|
| Mis WIs | `wit_my_work_items` | `project` |
| WIQL | `wit_query_by_wiql` | `project`, `wiql` (solo IDs) |
| Query guardada | `wit_get_query_results_by_id` | `project`, `query_id` |
| Detalle en lote | `wit_get_work_items_batch_by_ids` | `project`, `ids`, `fields` |
| Por iteración | `wit_get_work_items_for_iteration` | `project`, `iteration` |
| Query guardada (info) | `wit_get_query` | `project`, `query_id` o ruta |

## Common Mistakes

| Error | Regla |
|-------|-------|
| Inventar nombres de tools o leer catálogos externos en runtime | Usar solo los nombres de la tabla *Quick Reference* de esta skill; si falta una operación, decirlo |
| REST + PAT o `az` CLI como primera opción | MCP `ado` primero (maneja su propia auth) |
| Olvidar `project` en las llamadas | `project` = `{project_wi}` en TODA llamada |
| Esquema de config inventado (`organizacion`, `proyecto`) | Campos reales: `user_email`, `project_map.workitems`, `default_query`, `config_extras` |
| Improvisar onboarding sin perfil | Profile guard → `ado-profile-setup` |
| `expand: Relations` | Falla por tamaño; usa WIQL `[System.Parent] IN (...)` |
| Copiar descripciones o AC largos | Ficha compacta; resume |
| Modificar WIs durante la consulta | Solo lectura; crear/comentar → `ado-task-creator` / `ado-wi-comments` |
| Pedir organización/proyecto al usuario | Ya vienen del perfil; nunca pedirlos a mano |
