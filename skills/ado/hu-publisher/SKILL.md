---
name: ado-hu-publisher
description: >-
  Use when the user wants to publish a locally written User Story (HU) to Azure DevOps,
  sync a markdown-drafted story to ADO, or create a User Story from a local file.
  Triggers on "publish HU", "push HU to ADO", "create user story from file",
  "sync local story", "subir HU", "publicar historia de usuario", or providing a local HU path.
ready: true
---

# ADO HU Publisher

Publishes locally drafted User Stories (Markdown) to Azure DevOps: parse → preview → confirm → create.

## When to Use

- User has a markdown HU file and wants it in ADO
- User wants to sync a local draft that may already exist in ADO
- User mentions creating a User Story from a file

**When NOT to use:**

- Editing a work item already in ADO (use work item update tools)
- Creating a blank HU directly in ADO without a local file

## Context Injection

Reads `project_name`, `user_email`, `config_extras` (area, iteration, estimation, tags, process type) from `memory_skill.json` → `[ado].config.perfiles[perfil_activo]` (standalone).

## Core Flow

Three phases: **Parse locally → Confirm → Create in ADO.**

### Phase 1 — Parse and preview locally (zero ADO calls)

1. **Read & detect** file format (see [references/supported-formats.md](references/supported-formats.md)).
2. **Duplicate guard:** If real ADO ID exists, offer update instead — see [references/supported-formats.md](references/supported-formats.md).
3. **Extract fields** via progressive priority map — see [references/extraction-map.md](references/extraction-map.md).
4. **INVEST narrative guard** — see [references/invest-guard.md](references/invest-guard.md).
5. **Process detection** — see [references/process-detection.md](references/process-detection.md).
6. **Request missing required fields**, show preview with confidence, require `[S]` confirmation.

### Phase 2 — Create in ADO (only after `[S]`)

Validate `System.AssignedTo` via `ado_core_get_identity_ids`, create `User Story` via `ado_wit_work_item_write`, link parent if detected, report result.

### Phase 3 — Stamp local file

Insert publication seal under H1 with ADO ID, link, date. Preserve existing `ID Original` fields.

## Story Point Derivation

Estimation field varies by ADO process. See [references/sp-derivation.md](references/sp-derivation.md) for the parametrized derivation logic driven by `config_extras`.

| Process | ADO Field | Derivation |
|---------|-----------|------------|
| Agile | `StoryPoints` | Hours → SP via configurable conversion factor |
| Scrum | `Effort` | Hours directly (no conversion) |
| CMMI | `Size` | Abstract points (like Agile) |

## Quick Reference

| Issue | Resolution |
|-------|------------|
| Title > 255 chars | Truncate and warn |
| ADO fields need HTML | Convert `- [ ]` to `<li>`, use `<h3>`, `<p>`, `<ul>` |
| Parent ID has `#` prefix | Extract digits only |
| User Story type rejected | Try localized name or query `ado_wit_work_item_type` |

## Common Mistakes

- **Publishing without `[S]` confirmation:** Phase 1 is parse-only — never write to ADO without approval.
- **Skipping duplicate guard:** Always check for existing ADO ID before creating.
- **Sending Markdown to ADO fields:** `AcceptanceCriteria` and `Description` require HTML conversion.
- **Overwriting `ID Original` when stamping:** The seal is a separate block — preserve original fields.
- **Hardcoding estimation:** Always read conversion rules from `config_extras` — never assume a fixed method.
