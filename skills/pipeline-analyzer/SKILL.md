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

Reads `project_name` (from `project_map.repos`/`pipelines`) and `base_reports_path` from `memory_skill.json` → `[ado].config.perfiles[perfil_activo]` (standalone).

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

Key fields from run metadata: `id`, `state`, `result`, `createdDate`, `finishedDate`, `triggerInfo`.

### Phase C — Classify findings

| Category | Examples |
|----------|----------|
| Error | Failed tasks, non-zero exit codes, exceptions |
| Warning | Failed tests, low coverage, deprecated deps |
| Info | Included changes, duration, stages executed |
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
| 401/403 from tools | Inform user of insufficient permissions |

## Common Mistakes

- **Confusing pipeline ID with build/run ID:** `definitionId` is fixed per pipeline; `runId` changes per execution.
- **Showing full logs unprompted:** Only fetch detailed logs when user explicitly asks.
- **Skipping empty changes:** Some builds (scheduled, auto-triggered) have no commits — report "No changes detected".
- **Assuming in-progress builds are complete:** Always check `state` before reporting final results.
