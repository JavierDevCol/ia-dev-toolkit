---
name: transversales-workitems
description: "Crea, actualiza y verifica work items de la célula transversal BMM en Azure DevOps (Feature 128821, org GestionRequerimientos, proyecto FINTIA) haciendo cumplir el protocolo de incidentes vía el MCP de Azure DevOps apuntando al proyecto FINTIA (servidor bmm-dashboard-devops-mcp). Soporta incidentes nuevos e incidentes ya resueltos (registro retroactivo). Activa cuando el usuario diga: crear/registrar work item transversal, registrar incidente nuevo o ya resuelto, crear ticket transversal, levantar bug, actualizar work item, verificar work item, validar ticket contra el protocolo, revisar si el work item cumple el protocolo."
compatibility: Requires Azure DevOps MCP server, FINTIA project
argument-hint: "crear | actualizar <id> | verificar <id> — y los datos del incidente"
user-invocable: true
---

# transversales-workitems — Work Items de la Célula Transversal (BMM)

Gestiona work items **exclusivamente de la célula de temas transversales** de
BancaPorWhatsapp, conectada en vivo a Azure DevOps por MCP. Hace cumplir el
**protocolo del cliente** al pie de la letra en cada creación, actualización o verificación.

> **Fuente de verdad del protocolo:** [`Doc_BancaPorWhatsapp/docs/procedimientos/protocolo-icidentes.md`](../../../Doc_BancaPorWhatsapp/docs/procedimientos/protocolo-icidentes.md)
> Si el protocolo cambia, ese documento manda — esta skill solo lo operacionaliza.

## Requisito mandatorio: MCP de Azure DevOps apuntando a FINTIA

Todo el trabajo es **contra la plataforma vía MCP**. El cliente concentra **todos los
work items en un único proyecto de boards: `FINTIA`** (los demás proyectos son para
soluciones de software, repos, pipelines). Por eso esta skill **debe** usar un servidor
MCP de Azure DevOps cuyo `AZURE_DEVOPS_DEFAULT_PROJECT` sea **`FINTIA`** —
en este repo es el servidor **`bmm-dashboard-devops-mcp`**.

> ⚠️ **No usar** `bmm-devops-mcp` (apunta a `BancaPorWhatsappCICD`, que es para software,
> no para boards). Usar ese servidor registraría los work items en el proyecto equivocado.

- Antes de cualquier operación, confirmar que las herramientas `mcp__bmm-dashboard-devops-mcp__*`
  están disponibles. Si no lo están, **detenerse** y pedir al usuario que configure el MCP
  apuntando a `FINTIA` (remitir al [README.md](./README.md)). No inventar ni simular resultados.

## Contexto fijo (no cambiar)

| Atributo       | Valor                     | Nota                                                       |
| -------------- | ------------------------- | ---------------------------------------------------------- |
| `organizationId` | `GestionRequerimientos` | Default del MCP, pasar explícito igual.                    |
| `projectId`    | `FINTIA`                  | El servidor correcto (`bmm-dashboard-devops-mcp`) ya lo tiene por default; **pasarlo explícito igual** como salvaguarda. |
| Feature padre  | `128821`                  | Todo WI se enlaza como **hijo** de este Feature.           |
| Equipo         | `FINTIA Team`             | Area/Iteration por defecto del equipo.                     |

Tipos de WI permitidos: **Bug** (incidente), **Task**, **User Story**, **Issue**.

## Modos de operación

El usuario invoca con `crear`, `actualizar <id>` o `verificar <id>`. Si no lo dice, preguntar.

### Modo CREAR

Cubre **dos casos**: incidente **nuevo** (aún sin resolver) e incidente **ya resuelto**
(registro retroactivo). Preguntar al usuario cuál es si no lo indica.

1. **Recolectar** todos los campos del protocolo. Usar el checklist de
   [`references/checklist-protocolo.md`](./references/checklist-protocolo.md).
   Si falta cualquier dato obligatorio, **preguntar al usuario antes de crear** —
   nunca crear un WI incompleto ni rellenar con suposiciones.
   - Si es **retroactivo**, pedir además la **Resolución** (causa raíz, solución aplicada,
     fecha/hora de resolución, ambiente(s) donde se aplicó) — ítems 14–15 del checklist.
2. **Validar prioridad** contra la matriz P1–P4 (ver checklist) y el responsable (assignedTo).
3. **Construir la descripción** en HTML con la plantilla de
   [`references/mapeo-campos.md`](./references/mapeo-campos.md) (las 3 preguntas + contexto +
   evidencias + solicitante; el bloque **Resolución** solo si es retroactivo). HTML obligatorio.
4. **Crear** con `mcp__bmm-dashboard-devops-mcp__create_work_item`:
   - `organizationId: "GestionRequerimientos"`, `projectId: "FINTIA"`
   - `parentId: 128821` (enlaza al Feature automáticamente)
   - `workItemType`, `title`, `assignedTo`, `priority` (1–4), `tags`, `description` (HTML)
   - Mapeo exacto campo→Azure DevOps en [`references/mapeo-campos.md`](./references/mapeo-campos.md).
5. **Si es retroactivo**, llevar el WI a estado resuelto con
   `mcp__bmm-dashboard-devops-mcp__update_work_item` (`state: "Resolved"` o `"Closed"`) —
   `create_work_item` no recibe `state`.
6. **Confirmar** devolviendo el ID y la URL del WI creado, y correr una verificación rápida
   (modo VERIFICAR) sobre el WI recién creado.

### Modo ACTUALIZAR `<id>`

1. Leer el WI actual con `mcp__bmm-dashboard-devops-mcp__get_work_item` (`expand: "all"`).
2. Aplicar solo los cambios pedidos con `mcp__bmm-dashboard-devops-mcp__update_work_item`
   (usar `tagsToAdd`/`tagsToRemove` para no pisar tags existentes; usar `additionalFields`
   para campos no mapeados).
3. Si el WI **no cuelga** del Feature 128821, enlazarlo:
   `mcp__bmm-dashboard-devops-mcp__manage_work_item_link` con
   `sourceWorkItemId: <id>`, `targetWorkItemId: 128821`,
   `relationType: "System.LinkTypes.Hierarchy-Reverse"`, `operation: "add"`.
4. Re-verificar al final (modo VERIFICAR).

### Modo VERIFICAR `<id>`

1. Leer el WI con `get_work_item` (`expand: "all"`).
2. Recorrer el [`references/checklist-protocolo.md`](./references/checklist-protocolo.md) punto por punto.
3. Devolver un **reporte de cumplimiento**: ✅ cumple / ❌ falta, por cada ítem, con el detalle
   de qué corregir. No modificar nada en este modo salvo que el usuario lo pida.

## Reglas de comportamiento

- **Alcance:** solo work items de la célula transversal (hijos del Feature 128821). No tocar
  otros features/proyectos.
- **Nunca** crear o cerrar un WI sin **responsable** asignado.
- **Nunca** inventar datos del protocolo (usuarios afectados, fecha de detección, evidencias):
  si faltan, pedirlos.
- **Producción** requiere doble check: si el ambiente es Producción, advertirlo explícitamente
  en el reporte.
- Usar **siempre** el servidor `bmm-dashboard-devops-mcp` (apunta a `FINTIA`) y pasar
  `projectId: "FINTIA"` explícito en cada llamada como salvaguarda.
- Toda salida final incluye **ID + URL** del work item.
