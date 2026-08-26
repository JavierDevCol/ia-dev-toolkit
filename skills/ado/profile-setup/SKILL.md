---
name: ado-profile-setup
description: >
  Crea un nuevo perfil en config_consultas.json. Activa esta skill cuando
  config_consultas.json no exista, el perfil activo este incompleto o invalido,
  o el usuario quiera agregar un nuevo perfil.
  Triggers on: configurar perfil, nuevo perfil, setup agente,
  inicializar, config no existe, >nuevo-perfil.
compatibility: Requires Azure DevOps MCP server configured
---

## FASE 1 — DATOS BASICOS DEL PERFIL

PEDIR NOMBRE PERFIL → NOMBRE
PEDIR EMAIL ADO → EMAIL
PEDIR PROYECTO WORK ITEMS ADO → PROJ_WI
PEDIR PROYECTO REPOS/PRs ADO → PROJ_REPOS ([=] → copiar PROJ_WI)
PEDIR RUTA ABSOLUTA REPORTES → RUTA

## FASE 2 — CONFIGURACION DE CONSULTA (default_query)

> **🤷 ¿Cómo deseas configurar la búsqueda de tus Work Items?**
> - 📂 [A] **Tengo una query guardada en ADO** — dame el query ID o ruta
> - 🔗 [B] **Tengo un WI de ejemplo** — pega la URL o ID del WI
> - ✏️ [C] **Configurar manualmente** — cuestionario de filtros

### CASO A — Query guardada en ADO

PEDIR query_id O query_path (ruta tipo "Shared Queries/MiQuery")
PEDIR proyecto de la query (DEFAULT: PROJ_WI)

```json
"default_query": {
  "nombre": "NOMBRE_QUERY",
  "tipo": "saved_query",
  "proyecto": "PROJ_WI",
  "query_id": "QUERY_ID"
}
```

### CASO B — WI de ejemplo (URL o ID)

PEDIR URL o ID del WI.
EJECUTAR ado/wit_get_work_item(id) O curl REST API PARA EXTRAER:
- System.WorkItemType → tipos
- System.AreaPath → area_path
- System.Tags → tags (split por coma)
- System.Parent → parent_id
- System.State → estados de referencia

MOSTRAR RESUMEN LEGIBLE:
```
📋 Consulta construida desde WI #[ID]:

Se buscarán Work Items que:
  ✓ Estén asignados a ti ({EMAIL})
  ✓ Sean de tipo: {tipos}
  ✓ Tengan el tag: "{tags}"
  ✓ Estén en el área: {area_path}
  ✓ Proyecto: {PROJ_WI}
  ✓ No estén en estado: Closed, Done, Removed
```

> **🤷 ¿Esta consulta es correcta?**
> - ✅ [S] Sí, guardar como mi consulta por defecto
> - ✏️ [E] Editar algún filtro
> - 🔍 [V] Ver WIQL generado
> - ❌ [N] Cancelar

SI [E]: PREGUNTAR CUAL FILTRO MODIFICAR.
SI [V]: MOSTRAR WIQL CRUDO.
SI [S]: CONSTRUIR WIQL Y GUARDAR.

```json
"default_query": {
  "nombre": "Desde WI #{ID}",
  "tipo": "wiql",
  "proyecto": "PROJ_WI",
  "query": "SELECT ... FROM WorkItems WHERE ...",
  "resumen_legible": "WIs asignados a mí en {PROJ_WI}, tipo {tipos}, tag {tags}, excluye Closed/Done/Removed",
  "origen": {
    "tipo": "wi_ejemplo",
    "wi_id": ID,
    "wi_url": "URL"
  }
}
```

### CASO C — Cuestionario manual

PREGUNTAR SECUENCIALMENTE:

1. **Tipos de WI:**
   > ¿Qué tipos de Work Items buscar?
   > - [1] Bug
   > - [2] Task
   > - [3] User Story
   > - [4] Todos
   > - ✏️ [E] Otro (especificar)
   → DEFAULT: ["Bug", "Task"]

2. **Estados:**
   > ¿Qué estados incluir?
   > - [1] Active, New, To Do (abiertos)
   > - [2] Todos excepto Closed/Done
   > - ✏️ [E] Especificar
   → DEFAULT: excluir ["Closed", "Done", "Removed"]

3. **Asignado:**
   > ¿Solo WI asignados a ti?
   > - ✅ [S] Sí (recomendado)
   > - ❌ [N] No, todos del proyecto
   → DEFAULT: Sí (@me)

4. **Tags (opcional):**
   > ¿Filtrar por etiquetas? (ej: "Transversal-Incidencia")
   > - ✏️ [E] Ingresar tags
   > - ❌ [N] No filtrar por tags
   → DEFAULT: no filtrar

5. **Área (opcional):**
   > ¿Filtrar por área específica?
   > - ✏️ [E] Ingresar area_path
   > - ❌ [N] No filtrar por área
   → DEFAULT: no filtrar

6. **Parent (opcional):**
   > ¿Solo hijos de un WI específico?
   > - ✏️ [E] Ingresar ID del padre
   > - ❌ [N] No filtrar por padre
   → DEFAULT: no filtrar

7. **Iteración (opcional):**
   > ¿Filtrar por sprint/iteración?
   > - ✏️ [E] Ingresar iteration_path
   > - ❌ [N] No filtrar por iteración
   → DEFAULT: no filtrar

CONSTRUIR WIQL CON FILTROS SELECCIONADOS.
MOSTRAR RESUMEN LEGIBLE (FORMATO CASO B).
CONFIRMAR.

```json
"default_query": {
  "nombre": "Consulta personalizada",
  "tipo": "wiql",
  "proyecto": "PROJ_WI",
  "query": "SELECT ... FROM WorkItems WHERE ...",
  "resumen_legible": "WIs asignados a mí en {PROJ_WI}, tipo {tipos}, ..."
}
```

## FASE 3 — ESCRIBIR JSON

LEER config_consultas.json raiz workspace
NO EXISTE: CREAR JSON PLANTILLA
EXISTE JSON VALIDO: INSERTAR NOMBRE, ACTIVAR NOMBRE, NO MODIFICAR RESTO
EXISTE JSON INVALIDO: PREGUNTAR SOBRESCRIBIR, NO → CANCELAR

ESCRIBIR config_consultas.json 2 ESPACIOS INDENTACION:

```json
{
  "perfil_activo": "NOMBRE",
  "perfiles": {
    "NOMBRE": {
      "user_email": "EMAIL",
      "project_map": {
        "workitems": "PROJ_WI",
        "repos": "PROJ_REPOS",
        "pipelines": "PROJ_REPOS",
        "wiki": "PROJ_WI",
        "testplans": "PROJ_WI",
        "default": "PROJ_WI"
      },
      "base_reports_path": "RUTA",
      "default_query": {
        "nombre": "NOMBRE_QUERY",
        "tipo": "saved_query|wiql",
        "proyecto": "PROJ_WI",
        "query_id": "SOLO SI tipo=saved_query",
        "query": "SOLO SI tipo=wiql",
        "resumen_legible": "DESCRIPCION LEGIBLE DE LA CONSULTA",
        "origen": {
          "tipo": "manual|wi_ejemplo",
          "wi_id": "SOLO SI origen=wi_ejemplo",
          "wi_url": "SOLO SI origen=wi_ejemplo"
        }
      },
      "config_extras": {
        "formato_fecha": "ISO-8601",
        "idioma_reportes": "es"
      }
    }
  }
}
```

CONFIRMAR USUARIO: NOMBRE ACTIVADO, RESUMEN DE default_query.
