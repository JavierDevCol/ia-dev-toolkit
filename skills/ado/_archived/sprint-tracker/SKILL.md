---
name: ado-sprint-tracker
description: >
  Consulta de Work Items en Azure DevOps. Usa esta skill cuando el usuario
  quiera consultar su trabajo, ver resumen de WIs asignados, o sincronizar
  datos con ADO. También activa cuando mencione: mis HUs, mis bugs, mis
  tareas, consultar trabajo, mis WIs, ver trabajo, resumen de trabajo,
  sincronizar, generar histórico. Also triggers on: my work items, work
  report, sync work items, consultar trabajo.
compatibility: Requires Azure DevOps MCP server configured
---

## CONTEXTO

Esta skill lee del perfil activo (standalone) en `memory_skill.json` → `[ado].config.perfiles[perfil_activo]`:
- `project_name` — proyecto ADO resuelto desde `project_map.workitems`
- `user_email` — email del perfil activo
- `default_query` — configuración de consulta del perfil activo

La skill lee el perfil activo desde `memory_skill.json` → `[ado].config.perfiles[perfil_activo]` (standalone).

## CONSULTAR_TRABAJO

### FASE A — Ejecutar consulta en ADO

1. LEER default_query DEL CONTEXTO INYECTADO
2. SI default_query NO EXISTE O VIENE VACIO: DETENER Y PEDIR CONFIGURAR PERFIL (>nuevo-perfil)

3. SEGÚN default_query.tipo:

   **tipo = saved_query:**
   - EJECUTAR ado/wit_get_query_results_by_id(id=default_query.query_id, project=default_query.proyecto)
   - SI FALLA (query no existe, permisos): INFORMAR Y SUGERIR RECONFIGURAR PERFIL

   **tipo = wiql:**
   - EJECUTAR ado/wit_query_by_wiql(wiql=default_query.query, project=default_query.proyecto)
   - SI FALLA (WIQL inválido, permisos): INFORMAR Y SUGERIR RECONFIGURAR PERFIL

4. RESULTADO: LISTA DE WORK ITEMS
5. FILTRAR POR user_email SI default_query NO TIENE filtro.asignado = "todos"
6. CLASIFICAR POR TIPO: HUs 📘, Bugs 🐞, Tasks 🧩, Otros 📋

### FASE B — Mostrar resumen en chat

1. MOSTRAR TABLA DE RESULTADOS:
   | ID | Tipo | Título | Estado | Asignado | Padre |
2. MOSTRAR RESUMEN:
   - TOTAL ITEMS
   - DESGLOSE POR TIPO (HU/BUG/TASK/OTROS)
   - DESGLOSE POR ESTADO
   - RATIO SALUD (abiertos vs cerrados)
3. MOSTRAR RESUMEN LEGIBLE DE LA CONSULTA:
   > Consulta: {default_query.nombre}
   > {default_query.resumen_legible si existe}

## TRIGGERS SINONIMOS
Todos estos comandos ejecutan CONSULTAR_TRABAJO:
- consultar trabajo, mis WIs, mis bugs, mis tareas
- sincronizar, actualizar, refrescar
- generar histórico, ver trabajo

## REGLAS
SIEMPRE CONSULTAR ADO (NO USAR CACHE LOCAL, NO ARCHIVOS INDEX).
FILTRAR SIEMPRE POR user_email ACTIVO (SALVO QUE default_query.diga "todos").
USAR SIEMPRE default_query DEL CONTEXTO INYECTADO COMO CONSULTA OBLIGATORIA.
SI default_query.tipo = wiql: EJECUTAR EL WIQL TAL CUAL, NO MODIFICAR.
SI default_query.tipo = saved_query: USAR query_id, NO INTENTAR CONSTRUIR WIQL ALTERNATIVO.
