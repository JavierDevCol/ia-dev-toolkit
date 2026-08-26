---
name: bmm-crear-hu-devops
description: "Crea una Historia de Usuario (User Story) con sus tareas (Tasks) en Azure DevOps para el proyecto FINTIA, a partir de un archivo historia.md del ecosistema BancaPorWhatsapp de BMM. Úsala cuando el usuario pida crear, registrar o subir una HU a Azure DevOps / ADO. Solicita la URL del sprint, el correo del usuario asignado y la ruta al historia.md antes de hacer cualquier otra cosa."
compatibility: Requires Azure DevOps MCP server, BMM project context
---

# Skill: Crear HU y Tareas en Azure DevOps — BancaPorWhatsapp BMM

## Descripción

Crea en Azure DevOps (proyecto FINTIA) una Historia de Usuario con todas sus Tareas hijas, a partir del contenido de un archivo `historia.md`. Asigna todos los work items al usuario indicado y los ubica en el sprint especificado.

---

## PASO 1 – Recopilación de datos de entrada (OBLIGATORIO, hacer PRIMERO)

**Antes de leer cualquier archivo o hacer llamadas al ADO**, solicita al usuario los siguientes datos en un solo mensaje:

```
Para crear la HU y sus tareas en Azure DevOps necesito:

OBLIGATORIOS:
1. [SPRINT_URL]     URL del sprint donde se crearán los work items
                    Ejemplo: https://dev.azure.com/GestionRequerimientos/FINTIA/_sprints/taskboard/FINTIA%20Team/FINTIA/Sprint%204

2. [EMAIL_USUARIO]  Correo del usuario al que se asignarán la HU y todas las tareas
                    Ejemplo: dgalindez@bmm.com.co

3. [HISTORIA_PATH]  Ruta al archivo historia.md de la HU
                    Ejemplo: D:\BMM\Doc_BancaPorWhatsapp\docs\stories\WA2-003.3-simulacion-credito-servicio-core-bancario\historia.md

OPCIONALES:
4. [CERRAR]         ¿Cerrar los work items al crearlos? (s/n) — por defecto: n
                    Nota: cerrar la HU (User Story) requiere campos adicionales del proceso
                    de control de paso que debes completar manualmente en ADO.
```

Espera la respuesta completa del usuario antes de continuar.

---

## PASO 2 – Extraer datos del sprint

Con la `SPRINT_URL` proporcionada, extrae:

- **Proyecto ADO**: segmento de la URL (ej: `FINTIA`)
- **Nombre del sprint**: último segmento decodificado (ej: `Sprint 4`)
- **Iteration path**: formato `PROYECTO\\Sprint N` (ej: `FINTIA\\Sprint 4`)

Usa `mcp__ado__work_list_iterations` para listar los sprints del proyecto y encontrar el `path` exacto que coincida con el nombre del sprint de la URL.

---

## PASO 3 – Leer y analizar el historia.md

Lee el archivo en `HISTORIA_PATH` y extrae:

| Campo | Sección del historia.md |
|---|---|
| `TITULO_HU` | Línea `# Historia #...` o `## Historia de Usuario` |
| `DESCRIPCION_HU` | Sección `## Historia de Usuario` + `## Descripción` |
| `CRITERIOS_ACEPTACION` | Sección `## Criterios de Aceptación` |
| `TAREAS` | Sección `## Tareas de Implementación` o `refinamiento.md` si existe |

Para las tareas, agrúpalas por fase (Fase 0, Fase 1, etc.) o por tema lógico. Cada grupo se convierte en una Task hija. Si el historia.md tiene pocas tareas o no tiene sección de implementación, crea Tasks representativas basadas en los Criterios de Aceptación y la descripción técnica.

---

## PASO 4 – Obtener los campos obligatorios del proyecto

Antes de crear el work item, consulta un User Story existente en el proyecto para conocer los campos personalizados requeridos:

```
mcp__ado__wit_query_by_wiql:
  project: FINTIA
  wiql: "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = 'FINTIA' AND [System.WorkItemType] = 'User Story' ORDER BY [System.CreatedDate] DESC"
  top: 1
```

Luego lee ese work item con `mcp__ado__wit_get_work_item` expand=fields para ver los campos `Custom.*` requeridos y sus valores típicos.

Usa esos valores como referencia para los campos obligatorios al crear la HU nueva.

---

## PASO 5 – Crear la Historia de Usuario

Usa `mcp__ado__wit_create_work_item` con:

```
project: FINTIA
workItemType: "User Story"
fields:
  - System.Title: "[ID HU]: [TITULO_HU]"
  - System.IterationPath: "[ITERATION_PATH]"
  - System.AssignedTo: "[EMAIL_USUARIO]"
  - System.Description: "[DESCRIPCION_HU]"  (format: Markdown)
  - Microsoft.VSTS.Common.AcceptanceCriteria: "[CRITERIOS_ACEPTACION]"  (format: Markdown)
  - Microsoft.VSTS.Common.Priority: "2"
  - Microsoft.VSTS.Common.Risk: "B2"
  - Microsoft.VSTS.Common.ValueArea: "Business"
  # Campos Custom requeridos (usar valores del work item de referencia):
  - Custom.TipoSolicitud: "Requerimiento"
  - Custom.Gerencia: "Presidencia"
  - Custom.Categoria: "FINTIA"
  - Custom.AgenciaOficina: "100-Direccion General"
  - Custom.Impacto: "Alto"
  - Custom.ContieneReporte: "No"
  - Custom.Iniciativa: "NA"
  - Custom.AfectaOficinas: "false"
  - Custom.AfectaProcesos: "false"
  - Custom.ImpactoInterfaces: "false"
  - Custom.MiniProyecto: "false"
  - Custom.DeudaTecnica: "false"
  - Custom.Transacciones: "false"
  - Custom.SolicituddeFuenteBloqueada: "NO"
  - Custom.DefinicionGD: "false"
```

Guarda el `ID` del work item creado como `HU_ID`.

---

## PASO 6 – Crear las Tareas hijas

Agrupa las tareas del historia.md en máximo 8-10 Tasks por fase/tema. Usa `mcp__ado__wit_add_child_work_items` con:

```
parentId: HU_ID
project: FINTIA
workItemType: "Task"
items: (lista de tasks con title, description, iterationPath)
```

Cada task debe tener:
- `title`: `[Fase N] Descripción concisa` o `[Tema] Descripción`
- `description`: bullet list con los ítems específicos de esa fase/grupo
- `iterationPath`: mismo del sprint

---

## PASO 7 – Asignar usuario a las tareas (si no quedó en la creación)

Si las tareas no quedaron asignadas al usuario en el Paso 6, usa `mcp__ado__wit_update_work_items_batch` para asignar `EMAIL_USUARIO` a todos los IDs de las tareas:

```
updates: [
  {id: TASK_ID, path: "/fields/System.AssignedTo", value: "EMAIL_USUARIO"},
  ...
]
```

---

## PASO 8 – Cerrar work items (solo si CERRAR = "s")

Si el usuario solicitó cerrar los work items:

**Tareas:** Usa `mcp__ado__wit_update_work_items_batch` para cambiar `System.State` a `"Closed"` en todos los task IDs. Esto funciona correctamente para Tasks.

**HU (User Story):** Informa al usuario que la HU **no puede cerrarse automáticamente** porque el proceso de cierre en FINTIA requiere completar campos adicionales del control de paso a producción (`URLDesarrollo`, `DesarrolloSeguro`, `Aplicativos`, `FechaEntregaDesarrollov2`, `Tipodedesarrollo`, entre otros). Debe cerrarse manualmente desde la UI de Azure DevOps completando el formulario de control de paso.

---

## PASO 9 – Resumen final

Presenta al usuario un resumen con:

```
✅ HU creada: #[HU_ID] — [TITULO_HU]
   Sprint: [SPRINT_URL]
   Asignada a: [EMAIL_USUARIO]

✅ Tareas creadas ([N] tasks):
   #[ID1] — [Título tarea 1]
   #[ID2] — [Título tarea 2]
   ...

🔗 Ver en ADO: https://dev.azure.com/GestionRequerimientos/FINTIA/_workitems/edit/[HU_ID]

⚠️  La HU debe cerrarse manualmente desde ADO completando el control de paso.
    (solo si CERRAR = "s")
```

---

## Notas importantes

- **No crees work items sin recopilar los 3 datos obligatorios del Paso 1.**
- El proyecto ADO siempre es `FINTIA` para el ecosistema BancaPorWhatsapp de BMM.
- Los campos `Custom.*` son requeridos por el proceso del banco — si alguno falla, busca el valor correcto en un work item existente del mismo sprint o proyecto.
- El cierre de Tasks sí funciona automáticamente; el cierre de User Stories requiere intervención manual.
- Si la historia.md no tiene sección de tareas, genera Tasks representativas basadas en los Criterios de Aceptación (una task por escenario o grupo de escenarios).
- Si el archivo `refinamiento.md` existe en el mismo directorio que `historia.md`, léelo también para extraer las tareas de implementación.
