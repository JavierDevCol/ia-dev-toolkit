---
name: transversales-workitems
description: Use when the user needs to create, update, or verify work items for the BMM transversal cell in Azure DevOps FINTIA project, including new incidents, retroactive incident registration, or protocol compliance checks against the incident checklist.
---

# Transversales Work Items

Manages work items for the BMM transversal cell in Azure DevOps via MCP (`bmm-dashboard-devops-mcp`), enforcing the incident protocol on every create, update, or verify operation.

> **Protocol source of truth:** [`Doc_BancaPorWhatsapp/docs/procedimientos/protocolo-icidentes.md`](../../../Doc_BancaPorWhatsapp/docs/procedimientos/protocolo-icidentes.md). If the protocol changes, that document supersedes this skill.

## When to Use

- User says: crear/registrar work item transversal, registrar incidente nuevo o ya resuelto
- User says: crear ticket transversal, levantar bug, actualizar work item
- User says: verificar work item, validar ticket contra el protocolo
- Commands: `crear | actualizar <id> | verificar <id>`

**NOT for:** Software project work items (use standard ADO skills), or any work outside the transversal cell scope.

## Prerequisites

MCP server `bmm-dashboard-devops-mcp` must be available with `AZURE_DEVOPS_DEFAULT_PROJECT=FINTIA`. Before any operation, confirm tools `mcp__bmm-dashboard-devops-mcp__*` are present — if not, stop and ask the user to configure the MCP pointing to `FINTIA`.

> Do **not** use `bmm-devops-mcp` (targets `BancaPorWhatsappCICD` for software, not boards).

## Context (fixed)

| Attribute | Value |
|-----------|-------|
| `organizationId` | `GestionRequerimientos` |
| `projectId` | `FINTIA` |
| Parent Feature | `128821` (all WIs linked as children) |
| Team | `FINTIA Team` |

Allowed WI types: **Bug**, **Task**, **User Story**, **Issue**.

## Implementation

### Mode: CREAR

Two sub-cases: **new** (unresolved) or **retroactive** (already resolved). Ask the user which if not stated.

1. Collect all protocol fields using [references/checklist-protocolo.md](references/checklist-protocolo.md). For retroactive, also ask for Resolution (root cause, fix applied, date/time, environment).
2. Validate priority against the P1–P4 matrix (see checklist) and `assignedTo`.
3. Build description in HTML using the template from [references/mapeo-campos.md](references/mapeo-campos.md).
4. Create via `mcp__bmm-dashboard-devops-mcp__create_work_item` with `organizationId`, `projectId`, `parentId: 128821`, and all mapped fields.
5. If retroactive: transition to Resolved/Closed via `update_work_item` (`state`).
6. Return ID + URL and run a quick verify (Mode: VERIFICAR).

### Mode: ACTUALIZAR `<id>`

1. Read current WI with `get_work_item` (`expand: "all"`).
2. Apply requested changes with `update_work_item` (use `tagsToAdd`/`tagsToRemove` to preserve existing tags).
3. If WI is not linked to Feature 128821, link it via `manage_work_item_link`.
4. Re-verify.

### Mode: VERIFICAR `<id>`

1. Read WI with `get_work_item` (`expand: "all"`).
2. Walk through [references/checklist-protocolo.md](references/checklist-protocolo.md) item by item.
3. Return compliance report: pass/fail per item with correction details. Do not modify unless asked.

## Rules

- **Scope:** only WIs that are children of Feature 128821 — do not touch other features/projects
- Never create or close a WI without an assigned responsible person
- Never invent protocol data (affected users, detection date, evidence) — ask if missing
- Production environment requires explicit double-check warning in the report
- Always pass `projectId: "FINTIA"` explicitly as a safeguard
- Final output always includes **ID + URL**

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using wrong MCP server | Always use `bmm-dashboard-devops-mcp` (FINTIA), never `bmm-devops-mcp` |
| Creating incomplete WIs | Run full checklist before creation — never fill gaps with assumptions |
| Forgetting retroactive state transition | `create_work_item` does not accept `state` — call `update_work_item` after |
| Skipping verify after create/update | Always run Mode: VERIFICAR as final step |
