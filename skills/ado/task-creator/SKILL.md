---
name: ado-task-creator
description: >
  Creación de tareas hijas en Azure DevOps en dos fases: diseño desde un
  archivo de contexto técnico, y creación en ADO. Analiza documentos
  para proponer subtareas, valida contra la HU padre, y crea work items vinculados.
  Usa esta skill cuando el usuario quiera agregar tareas a una User Story, crear
  tareas desde un documento técnico, planificar subtareas, o desglosar una HU en
  trabajo ejecutable. También activa cuando mencione: agregar tareas, crear
  subtareas, desglosar HU, agg-tarea, plan de trabajo, crear tareas desde archivo.
  Also triggers on: create child tasks, batch task creation, break down user story.
compatibility: Requires Azure DevOps MCP server configured
---

# ADO Task Creator

Creación de tareas hijas en Azure DevOps con flujo de dos fases: diseño y creación.

## Contexto del perfil activo

Esta skill recibe del agente orquestador el contexto ya resuelto:
- `project_name` — proyecto ADO resuelto desde `project_map.workitems`
- `user_email` — email del perfil activo
- `config_extras` — para reglas dinámicas de estimación, formato, etc.

La skill **no lee `config_consultas.json` directamente**. Todo el contexto es inyectado por el agente.

## Comando: AGG-TAREA [HU_ID] [archivo_contexto]

### Fase 1 — Diseño

**A. Análisis de Contexto:**
1. Lee el `[archivo_contexto]` con `read/readFile`.
2. Identifica los pasos técnicos, componentes o acciones discretas que constituyen subtareas.

**B. Validación de Identidad:**
1. Consulta `ado/wit_get_work_item` con `HU_ID` para validar que existe y es `User Story`.
2. Si no existe o no es User Story: informar y detener.

**C. Propuesta de Plan de Trabajo:**
Presenta en el chat una tabla con las tareas detectadas:

| # | Título | Descripción sugerida | Estimación |
|---|--------|---------------------|------------|
| 1 | [Título] | [Descripción] | [Horas/Puntos según config_extras] |

**D. Interacción por Ambigüedad:**
Si un punto del documento es vago, el agente se detiene y pregunta.

### Fase 2 — Confirmación y Creación en Lote

Tras validar todos los puntos, presenta el resumen y pregunta:
> **[S]** Sí, crear todas | **[E]** Editar lista | **[A]** Abortar

**Si el usuario elige [S]:**
1. Invoca `ado/wit_create_work_item` para cada tarea con:
   - `System.Title` — Título de la tarea
   - `System.Description` — Descripción
   - Relación `Parent` → `HU_ID`
   - `System.AssignedTo` → `user_email` del perfil activo
   - Campos adicionales según `config_extras`
2. Recoge los IDs reales devueltos por ADO.
3. Muestra resumen: IDs creados, vínculos, errores si los hubo.

## REGLAS
SIEMPRE CONSULTAR ADO (NO USAR CACHE LOCAL).
NUNCA crear tareas en ADO sin confirmación explícita [S].
Si una tarea falla en batch, continuar con las siguientes y reportar errores al final.
Verificar que `HU_ID` sea `User Story`. Si es Bug, informar pero permitir continuar.
