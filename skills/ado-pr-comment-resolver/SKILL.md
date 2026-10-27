---
name: ado-pr-comment-resolver
description: >
  Use when the user wants to resolve, address, or fix pending/active comment
  threads on an Azure DevOps Pull Request according to the team's coding
  standard. Triggers on: resolver comentarios PR, resolve PR comments,
  address review feedback, fix PR threads, atender comentarios de revisión.
ready: true
---

# ADO PR Comment Resolver

Resolves active/pending comment threads on an ADO PR by applying local code
fixes that comply with the team's coding standard, then replying and closing
each thread — one at a time, with explicit confirmation per thread.

## When to Use

- A PR has open review comments that need code fixes aligned with a coding standard
- Command: `RESOLVER-COMENTARIOS-PR [PR_ID_or_URL]`

**NOT for:** running a full PR review/analysis (use `ado-pr-reviewer` instead), PRs
outside ADO, or when there's no local clone of the repo to edit.

## Non-Negotiables

These are not defaults to override — baseline testing showed agents skip them
unless stated explicitly:

1. **Never commit or push.** Fixes are applied to the local working tree only.
   The user reviews `git diff` and pushes themselves.
2. **Never batch-resolve.** `ALL` in thread selection (Phase B) means "attempt
   all of these," not "apply without asking." Every single thread still gets
   its own apply/reply/resolve confirmation (Phase C.5).
3. **Never resolve a thread without reading its full comment history.** A
   later reply can redefine what's being asked — never act on just the first
   comment.

## Core Pattern

```
Input → Resolve PR → Confirm coding standard path → List + select threads
→ per thread: propose fix → apply locally → confirm → reply + Fixed/WontFix
→ summary (no commit/push)
```

## Implementation

### Context

Same as `ado-pr-reviewer`: reads the active profile (`ado.config.perfiles.<perfil_activo>`) for `project_name` and `user_email`.

Read the config with memctl (read-only; its output IS the answer; if memctl is missing (exit 127) read `.SAC/config/sac.json` with `jq`; on exit 1 (invalid or empty JSON) stop and tell the user: do not read or edit the file by hand; never invent values):

```sh
P=$(sh .SAC/memctl.sh get ado.config.perfil_activo)   # active profile name
sh .SAC/memctl.sh get ado.config.perfiles.$P.project_map.repos   # project_name; fallback: project_map.default
sh .SAC/memctl.sh get ado.config.perfiles.$P.user_email
sh .SAC/memctl.sh get ado.config.perfiles.$P.config_extras.coding_standards_path
```

`null` or exit 2 → not configured. Profile names must not contain `.` (memctl uses it as path separator).

**Profile guard:** if `perfil_activo` is null, its profile is missing, or no project resolves, stop and ask the user to run `ado-profile-setup`.

### Coding Standard Path [required gate]

1. Look up `config_extras.coding_standards_path` in the active profile (command above). A saved `"none"` counts as missing here.
2. **Always ask**, even if a path is already configured:
   > 📐 Usaré este coding standard: `[path]`. **[S]** Confirmar / **[O]** Dar otra ruta
3. If there's no configured path, or the file doesn't exist, ask directly for
   one. If the user has none, **stop** — this skill exists specifically to
   produce standard-compliant fixes, so it cannot proceed without a standard
   (unlike `ado-pr-reviewer`, which can skip standards checks and continue).

### Full Workflow

**[Phase-by-phase reference (A-D) →](references/resolve-phases.md)**

| Phase | Purpose |
|-------|---------|
| A | Resolve PR from ID/URL, get repo + branch info |
| B | List human-authored Active/Pending threads, let user pick which to tackle |
| C | Per thread: read full history, propose fix per standard, apply locally, confirm, reply + Fixed/WontFix |
| D | Chat summary: resolved/wontfix/left/skipped + reminder to review and push |

## Quick Reference

| Thread action | ADO calls | Code |
|---------------|-----------|------|
| `[A]` Apply | `..._thread_write` reply → update_status `Fixed` | Local edit kept |
| `[W]` Won't fix | `..._thread_write` reply (justification) → update_status `WontFix` | Any local edit reverted |
| `[E]` Leave for user | none | Any local edit reverted, thread stays Active |
| `[S]` Skip | none | Any local edit reverted |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Committing/pushing after applying fixes | Never — leave changes uncommitted for the user to review and push |
| Resolving every active thread without asking which ones | List first (Phase B), let the user choose or say `ALL` |
| Reading only the first comment in a thread | Pull the full thread via `list_comments` before deciding |
| Trusting the configured standard path without asking | Always show + confirm it with the user, every run |
| Marking a thread `Fixed` without replying first | Reply, then `update_status` — never resolve silently |
| Treating policy/build-service threads as resolvable | Filter to human-authored Active/Pending threads only |
| Editing before checking the working tree | Run `git status` and confirm the PR's source branch is checked out first |
| Skipping per-thread confirmation because the batch was pre-selected | Selecting threads in Phase B is not approval to write — confirm each one individually |
