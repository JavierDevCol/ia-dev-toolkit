---
name: ado
description: >-
  Use when the user interacts with Azure DevOps: PRs, User Stories, tasks,
  pipelines, or profiles. Triggers on "ado", "azure devops", "pull request",
  "user story", "pipeline", "work item", "profile", or ADO commands.
ready: true
---

# ADO Skills

Entry point for all Azure DevOps skills. Select the sub-skill that matches the user's intent.

## Available Sub-Skills

| Skill | Purpose |
|-------|---------|
| `ado-profile-setup` | Create or fix ADO profiles in `memory_skill.json` |
| `ado-pr-creator` | Create Pull Requests with duplicate detection |
| `ado-pr-reviewer` | Review PRs with coding standards and conflict detection |
| `ado-hu-publisher` | Publish local markdown HUs to ADO |
| `ado-task-creator` | Break down HUs into child tasks |
| `ado-pipeline-analyzer` | Analyze pipeline runs, failures, and logs |

## When to Use

- User mentions Azure DevOps, ADO, or pastes an ADO URL
- PR, HU, task, pipeline, or profile operations
- ADO-specific commands (`REVISAR-PR`, `PENDIENTES-PR`, `agg-tarea`, etc.)

## Quick Reference

1. **Identify intent** → match to sub-skill above
2. **Load sub-skill** → invoke `ado-{sub-skill}` directly
3. **Profile required** → most sub-skills read from `memory_skill.json` → `[ado].config.perfiles[perfil_activo]`
4. **No profile?** → run `ado-profile-setup` first
