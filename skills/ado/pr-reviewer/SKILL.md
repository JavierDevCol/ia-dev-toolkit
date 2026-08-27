---
name: ado-pr-reviewer
description: >
  Use when the user wants to review, analyze, or validate a Pull Request in Azure DevOps,
  check coding standards on changed lines, detect merge conflicts, or manage pending PR reviews.
  Triggers on: review PR, code review, PR analysis, check coding standards, merge conflicts,
  pull request review, validate PR, pending reviews.
---

# ADO PR Reviewer

Structured PR review in Azure DevOps with coding standards validation, merge conflict detection, and pending review tracking.

## When to Use

- PR review, code review, or analysis in Azure DevOps
- Validating changed lines against coding standards and architecture guides
- Detecting merge conflicts or managing pending reviews
- Commands: `REVISAR-PR [PR_ID_or_URL]` or `PENDIENTES-PR`

**NOT for:** PRs outside ADO, metadata-only reads, or no ADO MCP server.

## Core Pattern

```
Input → Resolve PR → Extract data → Load standards → Analyze → Report → Act
```

**Verdict actions:** Approve `[A]`, Comment `[G]`, Reject `[Z]`, Resolve `[R]`, Cancel `[C]`

## Implementation

### Context

Reads from `memory_skill.json` → `[ado].config.perfiles[perfil_activo]` (standalone):

| Field | Source |
|-------|--------|
| `project_name` | `project_map.repos` |
| `user_email` | `user_email` from active profile |
| `base_reports_path` | `base_reports_path` from active profile |

### Standards Configuration

Pass via `config_extras`: `coding_standards_path` and `architecture_guide_path` (use `[nombre_del_repo]` as placeholder). If files don't exist, skip standards — deliver conflicts + threads + health only.

### Report Paths

Reports go in the **PR author's** folder (not reviewer's):

| Concept | Pattern |
|---------|---------|
| Author Reviews | `[base_reports_path]/[project]/[author_email]/pr_reviews/` |
| Report File | `review_PR_[PR_ID]_[timestamp].md` |
| Pending | `[base_reports_path]/[project]/[user_email]/pr_reviews/pending_reviews.json` |

### Full Workflow

**[Phase-by-phase reference (A-F) with commands →](references/pr-review-phases.md)**

| Command | Purpose |
|---------|---------|
| `REVISAR-PR [PR_ID_or_URL]` | Full review workflow |
| `PENDIENTES-PR` | List/cancel/resume pending reviews |

## Quick Reference

| Verdict | Condition | Options |
|---------|-----------|---------|
| ✅ Aligned | 0 critical, 0 conflicts | `[A]` Approve, `[C]` Cancel |
| ⚠️ Conflicts | `mergeStatus = conflicts` | `[R]` Resolve, `[G]` Comment, `[C]` Cancel |
| 🚫 Non-compliant | Critical violations | `[G]` Comment, `[Z]` Reject, `[C]` Cancel |
| Mixed | Conflicts + violations | All applicable |

**Votes:** `Approved`, `ApprovedWithSuggestions`, `WaitingForAuthor`, `Rejected`, `NoVote`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Hardcoding local paths for standards | Use `config_extras` parameters |
| `git diff` with two dots (`..`) | Use three dots (`...`) for source-branch-only changes |
| Anchoring comments on unmodified code | Only `+` lines; extract from `@@ -X,Y +Z,W @@` headers |
| Including system threads in counts | Filter to human-authored threads only |
| Auto-voting without user confirmation | Every ADO action requires explicit user selection |
| Treating `mergeStatus = queued` as final | Inform user merge hasn't been evaluated |
| Skipping analysis when standards missing | Still run conflicts + threads + health (skip D.2 only) |
| Not stripping `refs/heads/` | Clean branch names before git commands |
