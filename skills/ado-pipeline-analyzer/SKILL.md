---
name: ado-pipeline-analyzer
description: >-
  Use when the user asks to analyze, inspect, or debug an Azure DevOps build or pipeline run.
  Triggers on requests like "analyze build", "why did the build fail", "check pipeline status",
  "review logs", "pipeline run details", "what happened in the build", or pasting a pipeline URL.
ready: true
---

# ADO Pipeline Analyzer

Analyzes Azure DevOps pipeline runs and produces a structured report with errors, warnings, and recommendations.

## When to Use

- Build failed and user wants to know why
- User asks to check pipeline status, stages, or specific jobs
- User provides an ADO build URL and wants details
- Reviewing which commits were included in a build
- Inspecting stage approvals, gates, or deployment jobs

**When NOT to use:**

- Creating or editing pipelines (use pipeline YAML tools directly)
- Comparing two builds side-by-side
- Monitoring builds in real-time

## Overview

Identifies the target build, fetches run metadata/changes/stages/logs, classifies findings, and writes a structured report.

## Context Injection

Reads the project and `base_reports_path` from the active profile. Project = `project_map.pipelines` (fallback `project_map.repos`, then `project_map.default`).

Read the config with memctl (read-only; its output IS the answer; if memctl is missing (exit 127) read `.SAC/config/sac.json` with `jq`; on exit 1 (invalid or empty JSON) stop and tell the user: do not read or edit the file by hand; never invent values):

```sh
P=$(sh .SAC/memctl.sh get ado.config.perfil_activo)   # active profile name
sh .SAC/memctl.sh get ado.config.perfiles.$P.project_map.pipelines   # fallback: project_map.repos, then project_map.default
sh .SAC/memctl.sh get ado.config.perfiles.$P.base_reports_path
sh .SAC/memctl.sh get usuario.nombre
sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos
```

`null` or exit 2 → not configured. Profile names must not contain `.` (memctl uses it as path separator).

**Profile guard:** if `perfil_activo` is null, its profile is missing, or no project resolves, stop and ask the user to run `ado-profile-setup`.

**Missing profile fields:** if `base_reports_path` (absolute path) is missing from the active profile, ask the user once and persist the answer to that profile in `.SAC/config/sac.json` (`ado.config.perfiles.<profile>`, editing only that section) so later runs don't ask again.

Tomar `usuario.nombre` → **`{{usuario.nombre}}`** (comando de arriba), necesario para firmar el reporte en la Fase D. Si está vacío, la clave no existe, o `usuario.incluir_firma_en_documentos` es `false`, omitir la firma; no inventar un nombre.

## Core Flow

### Phase A — Identify build and scope

Ask: **Pipeline** (name/ID), **Build** (run number/ID or "latest"), optional **branch** filter. General or specific stage/job analysis? Extract from ADO URLs if provided.

### Phase B — Fetch build data

| Step | Tool | Purpose |
|------|------|---------|
| B1 | `ado_pipelines_definition` (list) | Find pipeline `definitionId` |
| B2 | `ado_pipelines_run` (list/get) | Get run metadata: state, result, dates, trigger |
| B3 | `ado_pipelines_build` (get_changes) | Commits included, authors, messages |
| B4 | `ado_pipelines_build` (get_status) | Stage/job/task states, errors, durations |
| B5 | `ado_pipelines_build_log` (list/get_content) | Detailed logs — only on user request |
| B6 | `ado_pipelines_run` (get) + `ado_pipelines_build_log` (list/get_content) | Run integrity: cancelation + stage coverage (see below) |

Key fields from run metadata: `id`, `state`, `result`, `createdDate`, `finishedDate`, `triggerInfo`.

### Run integrity (always)

`Succeeded` certifies only what ran, not that every stage ran. Verify before classifying:

1. **Cancelation:** from `ado_pipelines_run (get)` read `result` (1=Succeeded, 2=PartiallySucceeded, 3=Failed, 4=Canceled) and `finishedDate`. If suspicious, read the tail of the last log (`ado_pipelines_build_log get_content`): a canceled run leaves truncated logs and `Finishing: ... canceled` markers; a natural end shows `Set build status for commit`.
2. **Stage coverage:** the expanded YAML is log 1 (`expandedYamlUrl` from `ado_pipelines_run (get)`); its `- stage:` / `- job:` / `condition:` lines are what the pipeline DECLARES. `ado_pipelines_build_log (list)` + each log head (`startLine: 0, endLine: 2`) shows `##[section]Starting: <job/step>` = what ACTUALLY ran. Declared stages with no logs are skipped (read their `condition:` to say why).
3. Report the gap as `N de M stages ejecutados` and list each skipped stage with its condition.

### Phase C — Classify findings

| Category | Examples |
|----------|----------|
| Error | Failed tasks, non-zero exit codes, exceptions, canceled runs |
| Warning | Failed tests, low coverage, deprecated deps, stages skipped by condition that the user expected to run |
| Info | Included changes, duration, stages executed, stages skipped by design |
| Success | Stages completed without issues |

### Phase D — Generate report

See [references/report-template.md](references/report-template.md) for the full report template structure. Report is saved as `PIPELINE-REPORT_{runId}.md`.

## Quick Reference

| Scenario | Action |
|----------|--------|
| Build not found | List recent runs for the pipeline, ask user to pick |
| Build still running | Show partial status, note report is preliminary |
| Logs truncated | Use `ado_pipelines_build_log` with specific `logId` per stage |
| Multi-stage with pending gates | Note in findings — may be approval-related, not error |
| Succeeded but stages missing | Report coverage `N de M stages`; never present the success as full validation |
| 401/403 from tools | Inform user of insufficient permissions |

## Common Mistakes

- **Confusing pipeline ID with build/run ID:** `definitionId` is fixed per pipeline; `runId` changes per execution.
- **Showing full logs unprompted:** Only fetch detailed logs when user explicitly asks.
- **Skipping empty changes:** Some builds (scheduled, auto-triggered) have no commits — report "No changes detected".
- **Assuming in-progress builds are complete:** Always check `state` before reporting final results.
- **Equating Succeeded with full success:** `result: 1` only certifies what executed. Always contrast the expanded YAML (declared stages) against the executed logs and report `N de M stages`.
