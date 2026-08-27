# Mapeo Protocolo → Campos de Azure DevOps

Cómo se traduce cada elemento del protocolo a la llamada del MCP
`mcp__bmm-dashboard-devops-mcp__create_work_item` / `update_work_item`.

## Tabla de mapeo

| Elemento del protocolo        | Campo / parámetro del MCP                          | Notas                                                                 |
| ----------------------------- | -------------------------------------------------- | --------------------------------------------------------------------- |
| Ubicación (Feature padre)     | `parentId: 128821`                                 | Enlaza como hijo. Siempre.                                            |
| Organización                  | `organizationId: "GestionRequerimientos"`          | Explícito.                                                            |
| Proyecto                      | `projectId: "FINTIA"`                              | Usar el servidor `bmm-dashboard-devops-mcp` (default FINTIA) y pasarlo explícito igual. |
| Título                        | `title`                                            | Claro y conciso: *qué falla + dónde*.                                |
| Descripción (3 preguntas)     | `description` (HTML)                                | Usar la plantilla HTML de abajo.                                     |
| Sistema / Aplicación          | `tags` (1 de la lista de sistemas)                 | También se repite en la descripción.                                |
| Ambiente                      | `tags` (1 de la lista de ambientes)                | También se repite en la descripción.                                |
| Prioridad (P1–P4)             | `priority` (1–4) + `tags` (etiqueta P-x)           | P1→1, P2→2, P3→3, P4→4.                                              |
| Responsable                   | `assignedTo` (email o nombre)                      | **Obligatorio.**                                                     |
| Usuarios afectados            | `description` (HTML)                               | Volumen + área.                                                      |
| Fecha y hora de detección     | `description` (HTML)                               | Momento exacto (para correlación en Splunk).                        |
| Evidencias técnicas           | `description` (HTML) + adjuntos                     | Capturas, logs, payloads, videos.                                   |
| Datos del solicitante         | `description` (HTML)                               | Nombre de contacto + área operativa.                                |
| Tipo de WI                    | `workItemType`                                     | `Bug` / `Task` / `User Story` / `Issue`.                            |
| Estado (si ya está resuelto)  | `state` (en `update_work_item`)                    | Retroactivo → `Resolved` o `Closed`. Nuevo → estado inicial por defecto. |
| Resolución (retroactivo)      | `description` (bloque HTML "Resolución")           | Causa raíz, solución, fecha/hora de resolución, ambiente(s).        |
| Tiempo de atención *(opcional, retroactivo)* | `description` (bloque Resolución) + `additionalFields: { "Microsoft.VSTS.Scheduling.CompletedWork": <horas> }` | Duración total detección→resolución. Pedirlo; no bloquear si no está disponible. Si el usuario lo da en días/horas, convertir a horas para `CompletedWork`. |

## Valores controlados para `tags`

**Sistema / Aplicación** (elegir 1): `Portal Clientes`, `App Móvil BMM`,
`Core Transaccional`, `APIs / Kong Gateway`, `WhatsApp`.

**Ambiente** (elegir 1, son **cinco**, en orden de promoción): `Desarrollo Ceiba`,
`Desarrollo Fintia`, `QA / Pruebas`, `Preproducción`, `Producción`.
Flujo: `Desarrollo Ceiba → Desarrollo Fintia → QA / Pruebas → Preproducción → Producción`.

**Prioridad** (elegir 1): `P1 - Crítico`, `P2 - Alto`, `P3 - Medio`, `P4 - Bajo`.

> Etiqueta de célula recomendada para distinguir el trabajo transversal: `Transversal`.

## Mapa de prioridad → campo `priority`

| Protocolo        | `priority` | Tag             |
| ---------------- | ---------- | --------------- |
| P1 — Crítico     | `1`        | `P1 - Crítico`  |
| P2 — Alto        | `2`        | `P2 - Alto`     |
| P3 — Medio       | `3`        | `P3 - Medio`    |
| P4 — Bajo        | `4`        | `P4 - Bajo`     |

## Plantilla HTML de la descripción

La `description` del MCP **debe ser HTML** (no Markdown, sin CDATA). Plantilla a rellenar:

```html
<h3>1. ¿Qué está ocurriendo actualmente?</h3>
<p>{{descripcion_actual}}</p>

<h3>2. ¿Qué se esperaba que ocurriera?</h3>
<p>{{comportamiento_esperado}}</p>

<h3>3. Pasos exactos para reproducir</h3>
<ol>
  <li>{{paso_1}}</li>
  <li>{{paso_2}}</li>
</ol>

<h3>Contexto técnico</h3>
<ul>
  <li><b>Sistema / Aplicación:</b> {{sistema}}</li>
  <li><b>Ambiente:</b> {{ambiente}}</li>
  <li><b>Prioridad:</b> {{prioridad}}</li>
</ul>

<h3>Soporte de diagnóstico y evidencias</h3>
<ul>
  <li><b>Usuarios afectados:</b> {{volumen_y_area}}</li>
  <li><b>Fecha y hora de detección:</b> {{fecha_hora}}</li>
  <li><b>Evidencias técnicas:</b> {{evidencias}}</li>
  <li><b>Solicitante:</b> {{nombre_contacto}} — {{area_operativa}}</li>
</ul>

<!-- SOLO para incidentes ya resueltos (registro retroactivo) -->
<h3>Resolución</h3>
<ul>
  <li><b>Causa raíz:</b> {{causa_raiz}}</li>
  <li><b>Solución aplicada:</b> {{solucion}}</li>
  <li><b>Fecha y hora de resolución:</b> {{fecha_hora_resolucion}}</li>
  <li><b>Ambiente(s) donde se aplicó:</b> {{ambientes_solucion}}</li>
  <li><b>Tiempo de atención:</b> {{tiempo_atencion}}</li>  <!-- opcional: ej. "3 días", "4 horas". Omitir el <li> si no se tiene el dato -->
</ul>
```

> Para **Bug**, los pasos de reproducción también pueden ir en el campo
> `Microsoft.VSTS.TCM.ReproSteps` vía `additionalFields` (HTML).
>
> El bloque **Resolución** se incluye **solo** cuando el incidente ya está resuelto
> (registro retroactivo). En ese caso, además, dejar el WI en estado Resolved/Closed
> (ver fila *Estado* en la tabla de mapeo).

## Ejemplo de llamada (CREAR un Bug)

```jsonc
// mcp__bmm-dashboard-devops-mcp__create_work_item
{
  "organizationId": "GestionRequerimientos",
  "projectId": "FINTIA",
  "parentId": 128821,
  "workItemType": "Bug",
  "title": "Error al generar certificados de ahorro en Portal Clientes BMM",
  "assignedTo": "responsable@ceiba.com.co",
  "priority": 2,
  "tags": ["Transversal", "Portal Clientes", "Producción", "P2 - Alto"],
  "description": "<h3>1. ¿Qué está ocurriendo actualmente?</h3><p>...</p>..."
}
```

## Registro retroactivo (incidente ya resuelto)

`create_work_item` **no** recibe `state`; el estado se ajusta en un segundo paso:

1. Crear el WI con la descripción que **incluye el bloque "Resolución"** (igual que el ejemplo anterior).
2. Llevarlo a estado resuelto con `mcp__bmm-dashboard-devops-mcp__update_work_item`:

```jsonc
{
  "workItemId": 130045,
  "state": "Resolved"   // o "Closed", según el flujo del equipo
}
```

> Conservar la **fecha de detección original** en la descripción; la fecha de resolución va
> en el bloque "Resolución", no la reemplaza.

## Enlazar un WI existente al Feature 128821

```jsonc
// mcp__bmm-dashboard-devops-mcp__manage_work_item_link
{
  "organizationId": "GestionRequerimientos",
  "projectId": "FINTIA",
  "sourceWorkItemId": 99999,        // el WI hijo
  "targetWorkItemId": 128821,       // el Feature
  "relationType": "System.LinkTypes.Hierarchy-Reverse",
  "operation": "add"
}
```
