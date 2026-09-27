# PR Review — Detailed Phase Reference (GitHub REST)

## Phase A — Input Resolution

1. **Parse input:**
   - **Pure number** (e.g. `123`): treat as `pull_number`, ask/resolve `owner/repo` from git remote.
   - **GitHub URL** (`https://github.com/{owner}/{repo}/pull/{number}`): extract `owner`, `repo`, `pull_number` directly from the path.
2. **Get PR:** `GET /repos/{owner}/{repo}/pulls/{pull_number}`.
   - If 404 → inform user and stop.

## Phase B — Data Extraction

**B.1 — PR Metadata** (from the PR object):
- `title`, `body`, author (`user.login`)
- Branches: `head.ref` → `base.ref` (already bare names, no `refs/heads/` prefix to strip)
- `state`, `mergeable_state` (`clean`/`dirty`/`unstable`/`blocked`/`behind`/`unknown`)
- `created_at` (calculate age in days)

**B.2 — Comments and reviews:**
- `GET /repos/{owner}/{repo}/pulls/{pull_number}/comments` — inline (diff-anchored) comments.
- `GET /repos/{owner}/{repo}/issues/{pull_number}/comments` — general PR-level comments (PRs are issues under the hood in GitHub's model).
- `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews` — approvals/change-requests with their state.
- No resolved/unresolved flag available (see "Known gap" in SKILL.md) — report raw counts.

**B.3 — PR Commits:**
`GET /repos/{owner}/{repo}/pulls/{pull_number}/commits` — sha, message, author per commit.

**B.4 — Diff (from the API, no local git needed):**

`GET /repos/{owner}/{repo}/pulls/{pull_number}/files` returns, per file: `filename`, `status` (`added`/`modified`/`removed`/`renamed`), `additions`, `deletions`, and a `patch` field with the actual unified diff for that file (unless the file is too large — `patch` is omitted above ~300 changed lines or for binaries; fall back to `git diff origin/{base}...origin/{head} -- {filename}` locally in that case).

Store internally:
- `archivos_tocados[]` — list of `{path, change_type, patch}`
- Filter out binaries, lockfiles, generated files before analysis.
- If >30 files touched, ask user for full or critical-only analysis.

**B.5 — Conflict detail:**

GitHub does **not** expose conflict markers or affected sections via REST — only the aggregate `mergeable_state`. If `dirty`:
- Report "conflicts detected, manual resolution required" without per-line detail (unlike ADO's `merge-tree` extraction).
- Optionally, if the user wants line-level detail, fall back to local git: `git fetch origin {base} {head}` then `git merge-tree $(git merge-base origin/{base} origin/{head}) origin/{base} origin/{head}`.

**B.6 — Previous pending review:**
Check `[Reviewer Pending Path]/pending_reviews.json` for a prior record of this PR number. If found, load as context for Phase D.

## Phase C — Load Team Standards

1. Read `[coding_standards_path]` and `[architecture_guide_path]` (asked once per session — see SKILL.md).
2. Consolidate into a validation context.

If `coding-standards.md` doesn't exist: skip to Phase D with only D.1 (conflicts) and D.3 (health), skip D.2.

## Phase D — Analysis

**D.1 — Merge conflicts:**
- `mergeable_state = clean` → 🟢 **No conflicts**
- `mergeable_state = dirty` → 🔴 **CONFLICTS DETECTED** (see B.5 — usually no per-line detail)
- `mergeable_state = unknown` → re-fetch the PR once (GitHub computes this async); if still `unknown`, report 🟡 **not yet evaluated**

**D.2 — Standards validation on changed code:**

Using `archivos_tocados[]` (`patch` field) and rules from Phase C, analyze **only added/modified lines** (lines starting with `+` in the patch, excluding the `+++` file header):

- Branch naming, commit messages, PR description quality
- File structure (new/moved files in expected directories)
- Naming, imports, patterns/anti-patterns per the architecture guide
- Documentation on new public methods

Classify: 🔴 Critical violation · 🟡 Warning · 🟢 Compliant. Record `{file, line, violated_rule, snippet, severity, explanation}` — `line` comes from parsing the `patch` hunk headers (`@@ -a,b +c,d @@`), counting from `c`.

**D.3 — General health:**
- Review-comment count (no resolved/unresolved split — see Known gap)
- Days PR has been open
- Coherence: title ↔ body ↔ linked issues (`Closes #N` mentions)
- Change volume: files/lines touched

## Phase E — Report and Actions

**E.1:** Build report using `assets/template-pr-review-report.md`, present in chat.

**E.2 — Verdict and options:** same four cases as `ado-pr-reviewer` (Aligned / Conflicts / Non-compliant / Mixed) — see SKILL.md Quick Reference.

## Phase F — Execute Selected Action

**[A] Approve:**
1. `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews` — body: `{"event": "APPROVE", "body": "✅ Code Review Approved — analyzed against coding-standards.md. No violations or conflicts."}`
2. Remove from `pending_reviews.json` if present.
3. Confirm: `✅ PR #[number] approved.` No report file generated.

**[G] Add comment:**
1. For findings anchored to code: `POST /repos/{owner}/{repo}/pulls/{pull_number}/comments` — body: `{"body": "...", "commit_id": "[head sha]", "path": "[file]", "line": N, "side": "RIGHT"}`.
2. For findings without a specific file/line (branch convention, commit messages): `POST /repos/{owner}/{repo}/issues/{pull_number}/comments` — body: `{"body": "..."}` (general comment).
3. Confirm counts (anchored vs. general).
4. Ask: generate report file? `[S]`/`[N]` — same as ADO version.

**[Z] Reject:**
Confirm `[S]`/`[N]` first. If confirmed:
`POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews` — body: `{"event": "REQUEST_CHANGES", "body": "🚫 Not Approved — violations found: [list]."}`

**[R] Resolve (conflicts):**
`POST /repos/{owner}/{repo}/issues/{pull_number}/comments` — body: `{"body": "⚠️ Merge conflicts detected. Manual rebase/merge of [base] into [head] required."}`

**[C] Cancel review:**
Append to `pending_reviews.json`:
```json
{
  "pr_number": "[number]",
  "titulo": "[title]",
  "pendiente_por": "[reason]",
  "responsable": "[user.login]",
  "rama_origen": "[head.ref]",
  "rama_destino": "[base.ref]",
  "fecha_revision": "[ISO timestamp]",
  "revisado_por": "[reviewer login]"
}
```

## PENDIENTES-PR Command

Same as `ado-pr-reviewer`: read `pending_reviews.json`, present table, offer `[R]` resume / `[D]` discard / `[N]` nothing.
