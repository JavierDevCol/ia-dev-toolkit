# Query Configuration — Interactive Prompts

## Main Menu

> **¿Cómo deseas configurar la búsqueda de tus Work Items?**
> - **[A]** Tengo una query guardada en ADO — dame el query ID o ruta
> - **[B]** Tengo un WI de ejemplo — pega la URL o ID del WI
> - **[C]** Configurar manualmente — cuestionario de filtros

## Case A — Saved Query

Ask for: `query_id` or `query_path` (e.g. `"Shared Queries/MiQuery"`), and project (default: `PROJ_WI`).

## Case B — WI Example

1. Ask for URL or ID of the WI.
2. Call `ado/wit_get_work_item(id)` or REST API to extract fields (see config-schema.md).
3. Show readable summary:

```
Consulta construida desde WI #[ID]:

Se buscarán Work Items que:
  ✓ Estén asignados a ti ({EMAIL})
  ✓ Sean de tipo: {tipos}
  ✓ Tengan el tag: "{tags}"
  ✓ Estén en el área: {area_path}
  ✓ Proyecto: {PROJ_WI}
  ✓ No estén en estado: Closed, Done, Removed
```

> **¿Esta consulta es correcta?**
> - **[S]** Sí, guardar como mi consulta por defecto
> - **[E]** Editar algún filtro
> - **[V]** Ver WIQL generado
> - **[N]** Cancelar

On [E]: ask which filter to modify. On [V]: show raw WIQL. On [S]: build WIQL and save.

## Case C — Manual Questionnaire

Ask sequentially:

1. **Tipos de WI:** Bug, Task, User Story, Todos, or custom → default: `["Bug", "Task"]`
2. **Estados:** Open only, all except Closed/Done, or custom → default: exclude `["Closed", "Done", "Removed"]`
3. **Asignado:** Only assigned to me? → default: Yes (`@me`)
4. **Tags (optional):** Filter by tags? → default: no filter
5. **Área (optional):** Filter by area_path? → default: no filter
6. **Parent (optional):** Only children of a specific WI? → default: no filter
7. **Iteración (optional):** Filter by sprint/iteration? → default: no filter

Build WIQL with selected filters. Show readable summary (Case B format). Confirm.

## Basic Data Prompts

| Field | Prompt | Default |
|-------|--------|---------|
| Profile name | Nombre del perfil | — |
| Email | Email de Azure DevOps | — |
| WI project | Proyecto para Work Items | — |
| Repos project | Proyecto para Repos/PRs | (= WI project) |
| Reports path | Ruta absoluta para reportes | — |
