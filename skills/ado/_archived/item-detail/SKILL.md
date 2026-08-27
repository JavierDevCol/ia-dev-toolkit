---
name: ado-item-detail
description: >
  Extracción y consulta detallada de ítems individuales de Azure DevOps
  (User Stories, Bugs, Tasks). Busca ítems por ID o palabra clave
  directamente en ADO. Usa esta skill cuando el usuario pida ver el
  detalle de un ítem, buscar una tarea, o consultar información de un
  work item. También activa cuando mencione: detalle ítem, detalle HU,
  ver bug, buscar tarea, información de la tarea. Also triggers on: item
  detail, work item info, search task, task detail.
compatibility: Requires Azure DevOps MCP server configured
---

## CONTEXTO

Esta skill lee del perfil activo (standalone) en `memory_skill.json` → `[ado].config.perfiles[perfil_activo]`:
- `project_name` — proyecto ADO resuelto desde `project_map.workitems`
- `user_email` — email del perfil activo

La skill lee el perfil activo desde `memory_skill.json` → `[ado].config.perfiles[perfil_activo]` (standalone).

## Comando: DETALLE_ITEM [ID o Palabra_Clave]

### Fase A — Consulta en ADO

1. SI input es ID numérico:
   - Invoca `ado/wit_get_work_item` con el ID
2. SI input es palabra clave:
   - Invoca `ado/search_workitem` con la palabra clave + filtros del proyecto

### Fase B — Extracción de datos

Extrae del resultado:
- Descripción — limpia de HTML, convierte a Markdown
- Criterios de Aceptación — lista de checkboxes
- Estimación — Story Points si aplica
- Comentarios — fecha, usuario y texto
- Relaciones — Padre, hijos
- Tags, Área, Iteración, Estado, Asignado

### Fase C — Resultado

Muestra detalle completo en el chat (NO genera archivos).

## Comando: BUSCAR-TAREA [ID o Palabra_Clave]

1. Invoca `ado/search_workitem` con la palabra clave
2. Muestra resultados:
   | ID | Tipo | Título | Estado | Asignado |
3. Si múltiples resultados: listar opciones y preguntar cuál ver en detalle
4. Si un resultado: mostrar detalle directamente

## REGLAS
SIEMPRE CONSULTAR ADO (NO USAR CACHE LOCAL).
Descripciones de ADO vienen en HTML. Limpiar antes de mostrar.
Buscar por palabra clave en Título Y Descripción.
Si la palabra clave devuelve múltiples resultados, listar opciones y preguntar.
