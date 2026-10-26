---
name: ado-profile-setup
description: Use when the active `[ado]` profile in memory_skill.json is incomplete or invalid, or the user wants to add a new Azure DevOps profile.
ready: true
---

# ADO Profile Setup

Creates and manages user profiles in `memory_skill.json` → section `[ado].config`, the central config that maps Azure DevOps email, projects, and default queries to an active profile.

## When to Use

- `memory_skill.json` lacks the `[ado]` section or has no `perfiles`
- Active profile has missing or invalid fields
- User requests a new profile (command: `>nuevo-perfil`)
- Agent needs project/email context before other ADO skills run

**NOT for:** Querying work items, creating WIs, or any operation that consumes profile data — use the corresponding skill instead.

## Implementation

### Phase 1 — Basic Data

Collect via interactive prompts:

| Field | Key | Notes |
|-------|-----|-------|
| Profile name | NOMBRE | — |
| ADO email | EMAIL | — |
| WI project | PROJ_WI | For work item queries |
| Repos/PR project | PROJ_REPOS | Default: copy PROJ_WI |
| Reports path | RUTA | Absolute path |

### Phase 2 — Default Query

Present three options (see [references/query-prompts.md](references/query-prompts.md) for full prompt flows):

| Option | Source | Output |
|--------|--------|--------|
| **[A]** Saved query | Query ID or path in ADO | `saved_query` type with `query_id` |
| **[B]** WI example | URL or ID of an existing WI | `wiql` type, auto-extracted fields |
| **[C]** Manual | Interactive questionnaire | `wiql` type, user-selected filters |

For **[B]**, call `ado/wit_get_work_item(id)` to extract type, area, tags, parent, and state — then show a readable summary for confirmation before saving.

### Phase 3 — Write JSON

- File: `memory_skill.json` at skills root, under `[ado].config`, 2-space indent
- Does not exist → create, insert new profile, set as active
- Exists valid → insert new profile, activate it, leave others untouched
- Exists invalid → ask to overwrite; if no → cancel

Full JSON schema: [references/config-schema.md](references/config-schema.md)

## Quick Reference

| Scenario | Action |
|----------|--------|
| First run (no config) | Phase 1 → 2 → 3 |
| Add profile to existing `[ado]` config | Phase 1 → 2, insert into `perfiles`, set `perfil_activo` |
| Fix broken `[ado]` config | Ask overwrite → Phase 1 → 2 → 3 |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Overwriting existing profiles | Always insert new profile key, never replace entire `perfiles` object |
| Skipping query confirmation | Always show readable summary before saving — never save unreviewed WIQL |
| Using wrong project for repos | `repos`/`pipelines` may differ from `workitems` — ask explicitly |
