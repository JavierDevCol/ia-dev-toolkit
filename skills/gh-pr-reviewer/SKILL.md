---
name: gh-pr-reviewer
description: >
  Use when the user wants to review, analyze, or validate a Pull Request on GitHub,
  check coding standards on changed lines, detect merge conflicts, or manage pending PR
  reviews. Triggers on: review PR, code review, PR analysis, check coding standards,
  merge conflicts, pull request review, validate PR, pending reviews (GitHub repo).
  Uses the raw GitHub REST API via curl + PAT (no gh CLI).
ready: true
---

# GitHub PR Reviewer

Structured PR review on GitHub with coding standards validation, merge conflict detection, and pending review tracking. Mirrors `ado-pr-reviewer` — same shape, different wire, one real gap noted below.

## When to Use

- PR review, code review, or analysis on a GitHub repo
- Validating changed lines against coding standards and architecture guides
- Detecting merge conflicts or managing pending reviews
- Commands: `REVISAR-PR [PR_number_or_URL]` or `PENDIENTES-PR`

**NOT for:** PRs outside GitHub (ADO → `ado-pr-reviewer`), metadata-only reads.

## Known gap vs. `ado-pr-reviewer`

ADO exposes thread resolution status (`Active`/`Fixed`/`Closed`) per review comment. **GitHub's REST API does not** — resolved/unresolved is only available via the GraphQL API (`reviewThreads.isResolved`), which is out of scope here (REST-only per this project's setup). D.3 below reports raw review-comment counts, not resolved/unresolved — flagged as a known simplification, not silently dropped.

## Core Pattern

```
Input → Resolve PR → Extract data → Load standards → Analyze → Report → Act
```

**Verdict actions:** Approve `[A]`, Comment `[G]`, Reject `[Z]`, Resolve `[R]`, Cancel `[C]`

## Auth

Same as `gh-pr-creator`: `curl -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" ...`

## Implementation

### Standards Configuration

Ask the user (once) for `coding_standards_path` and `architecture_guide_path`. If files don't exist, skip standards — deliver conflicts + comments + health only.

### Report Paths

Reports go in the **PR author's** folder (not reviewer's), same convention as `ado-pr-reviewer`:

| Concept | Pattern |
|---------|---------|
| Author Reviews | `[base_reports_path]/[repo]/[author_login]/pr_reviews/` |
| Report File | `review_PR_[number]_[timestamp].md` |
| Pending | `[base_reports_path]/[repo]/[reviewer_login]/pr_reviews/pending_reviews.json` |

### Full Workflow

**[Phase-by-phase reference (A-F) with endpoints →](references/pr-review-phases.md)**

| Command | Purpose |
|---------|---------|
| `REVISAR-PR [number_or_URL]` | Full review workflow |
| `PENDIENTES-PR` | List/cancel/resume pending reviews |

## Quick Reference

| Verdict | Condition | Options |
|---------|-----------|---------|
| ✅ Aligned | 0 critical, `mergeable_state = clean` | `[A]` Approve, `[C]` Cancel |
| ⚠️ Conflicts | `mergeable_state = dirty` | `[R]` Resolve, `[G]` Comment, `[C]` Cancel |
| 🚫 Non-compliant | Critical violations | `[G]` Comment, `[Z]` Reject, `[C]` Cancel |
| Mixed | Conflicts + violations | All applicable |

**Review events (GitHub):** `APPROVE`, `REQUEST_CHANGES`, `COMMENT`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Hardcoding local paths for standards | Ask once, reuse for the session |
| `git diff` with two dots (`..`) | Use three dots (`...`) for source-branch-only changes, if diffing locally |
| Anchoring comments on unmodified code | Only `+` lines; use `line`/`side: RIGHT` from the `/files` patch, never on untouched code |
| Treating `mergeable_state = unknown` as final | GitHub computes it async — re-fetch after a few seconds before reporting conflicts |
| Auto-reviewing without user confirmation | Every GitHub write action requires explicit user selection |
| Assuming resolved/unresolved thread status exists | It doesn't via REST — see "Known gap" above |
| Skipping analysis when standards missing | Still run conflicts + comments + health (skip D.2 only) |
