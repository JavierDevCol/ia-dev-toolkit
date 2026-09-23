---
name: ado-task-creator
description: Use when the user wants to add child tasks to a User Story, create subtasks from a technical document, break down a HU into executable work, or mentions commands like agg-tarea, crear tareas, or desglosar HU.
ready: true
---

# ADO Task Creator

Two-phase workflow for creating child tasks in Azure DevOps: design from a context file, then batch-create linked work items.

## When to Use

- User wants to add tasks to an existing User Story (`agg-tarea [HU_ID] [file]`)
- A technical document needs to be broken into discrete ADO tasks
- User says: agregar tareas, crear subtareas, desglosar HU, plan de trabajo

**NOT for:** Creating bugs, updating existing tasks, or querying work items — use `ado_wit_work_item_write` or `ado_wit_query` directly.

## Implementation

This skill reads the active profile + `config_extras` + `project_map` from `memory_skill.json` → `[ado].config.perfiles[perfil_activo]` (standalone). The user may provide project context explicitly, or it is read from the active profile.

### Phase 1 — Design

1. **Analyze context:** Read the provided file, identify discrete technical steps → candidate subtasks.
2. **Validate parent:** Call `ado_wit_work_item` with `HU_ID` — must be `User Story`. If not, warn but allow continuation.
3. **Propose plan:** Present table with #, title, suggested description, and estimation per `config_extras`.
4. **Resolve ambiguity:** If any point is vague, stop and ask before proceeding.

### Phase 2 — Confirm & Create

Present summary and ask: **[S]** Create all | **[E]** Edit list | **[A]** Abort

On **[S]**, for each task call `ado_wit_write` (`create`):
- `System.Title`, `System.Description`
- Parent link → `HU_ID`
- `System.AssignedTo` → `user_email`
- Additional fields per `config_extras`

Collect returned IDs and show summary (created IDs, links, any errors).

## Rules

- Always query ADO live — never use cached data
- Never create WIs without explicit `[S]` confirmation
- If one task fails in batch, continue with the rest and report errors at end
- Verify parent is User Story; if Bug, warn but allow

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating without confirmation | Always present summary and wait for `[S]` |
| Assuming parent type | Always call `ado_wit_work_item` to verify it is a User Story |
| Stopping on first batch error | Continue remaining tasks, report all errors at the end |
