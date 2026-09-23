# PR Review — Detailed Phase Reference

## Phase A — Input Resolution

1. **Parse input:**
   - **Pure number** (e.g. `12345`): treat as `pullRequestId`.
   - **ADO URL** (contains `_git/` and `pullrequest/`): extract `repositoryName` and `pullRequestId` from path.
2. **Resolve repository:**
   - If repo name available (from URL), call `ado/repo_get_repo_by_name_or_id` to get `repositoryId`.
   - If only numeric PR ID, call `ado/repo_list_pull_requests_by_repo_or_project` with `project_name` and status `All` to locate the PR and its `repositoryId`.
3. **Get PR:**
   - Call `ado/repo_get_pull_request_by_id` with `repositoryId`, `pullRequestId`, `includeWorkItemRefs = true`.
   - If PR doesn't exist or doesn't belong to active project → inform user and stop.

## Phase B — Data Extraction

**B.1 — PR Metadata** (from `get_pull_request_by_id`):
- Title, description, author (`createdBy.displayName` and `createdBy.uniqueName`)
- Branches: `sourceRefName` → `targetRefName` (strip `refs/heads/` prefix)
- Status: `status`, `mergeStatus`
- Linked Work Items
- Creation date (calculate age in days)

**B.2 — Threads and discussions:**
Call `ado/repo_list_pull_request_threads` and classify:
- Threads `Active` or `Pending` → **unresolved** discussions
- Threads `Fixed`, `Closed`, `WontFix` → **resolved** discussions
- Filter system threads (push notifications, policy checks) — count only human-authored ones.

**B.3 — PR Commits:**
Call `ado/repo_search_commits` filtering by source branch. Extract: short hash, message, author.

**B.4 — Diff (local git):**

```bash
# 1. Fetch both branches
git fetch origin [target_branch] [source_branch]

# 2. File list with change type
git diff origin/[target_branch]...origin/[source_branch] --name-status
```

Returns: `A` (added), `M` (modified), `D` (deleted), `R` (renamed).

For each modified/added file, get changed lines only:

```bash
# 3. Diff with context (5 lines)
git diff origin/[target_branch]...origin/[source_branch] -U5 -- [file_path]
```

Store internally:
- `archivos_tocados[]` — list of `{path, change_type, diff_content}`
- Only store diff for code files (filter out binaries, images, lockfiles).
- If >30 files touched, ask user for full or critical-only analysis.

**B.5 — Conflict detail** (if `mergeStatus = conflicts`):

```bash
# Get merge base
git merge-base origin/[target_branch] origin/[source_branch]

# Simulate merge for conflict info (read-only)
git merge-tree $(git merge-base origin/[target_branch] origin/[source_branch]) origin/[target_branch] origin/[source_branch]
```

From `merge-tree` output, extract:
- Files in conflict (marked `changed in both`)
- Sections with `<<<<<<<`, `=======`, `>>>>>>>` markers

If `merge-tree` unavailable (old git), fallback:
```bash
git diff origin/[target_branch]...origin/[source_branch] --check
```

Store: `conflictos[]` — list of `{path, conflict_detail, affected_section}`

**B.6 — Previous pending review:**
Check if `[Reviewer Pending Path]/pending_reviews.json` contains a prior record for this PR. If so, load as context for Phase D.

## Phase C — Load Team Standards

1. Read `[coding_standards_path]`.
2. Determine PR repository name (from Phase A).
3. Read `[architecture_guide_path]` (replacing `[nombre_del_repo]` with actual repo name).
4. Consolidate rules from both files into a validation context.

If `coding-standards.md` doesn't exist:
> Standards validation not possible. Deliver only PR summary (metadata, conflicts, threads) without code validation. Skip to Phase D with only D.1 (conflicts) and D.3 (general health). Don't run D.2.

If architecture guide doesn't exist:
> Architecture validation based solely on `coding-standards.md`.

## Phase D — Analysis

Execute four dimensions:

**D.1 — Merge conflicts:**
- `mergeStatus = succeeded` → 🟢 **No conflicts**
- `mergeStatus = conflicts` → 🔴 **CONFLICTS DETECTED** — use B.5 detail:
  - List each conflicted file with affected section
  - Brief probable cause explanation (both branches changed same lines)
  - Resolution direction if obvious
- `mergeStatus = queued` → 🟡 **Merge not yet evaluated by ADO**

**D.2 — Standards validation on changed code:**

Using `archivos_tocados[]` from B.4 and rules from Phase C, analyze **only the diff** (added/modified lines):

- **Branch naming:** Does source branch follow defined pattern? (e.g. `feature/`, `bugfix/`, `hu-[ID]-`)
- **Commit messages:** Do they follow Conventional Commits or defined convention?
- **PR description:** Is it descriptive and references work items?
- **File structure:** Are new/moved files in expected directories?
- **New/modified code** (only `+` lines in diff):
  - Naming: Do variables, functions, classes follow standard convention?
  - Imports: Does ordering and grouping follow the guide?
  - Patterns: Does it respect architecture defined in `architecture_*.md`? (e.g. layers, responsibilities)
  - Anti-patterns: Does it introduce patterns prohibited by the standard?
  - Documentation: Do new public methods have required documentation?

**Only analyze changed lines (`+`), never existing untouched code.**

Classify each finding:
- 🔴 **Critical violation** — Breaks mandatory standard
- 🟡 **Warning** — Minor deviation or recommendation
- 🟢 **Compliant** — Meets standard

For each finding, record: `{file, start_line, end_line, violated_rule, code_snippet, severity, explanation}`

**D.3 — General health:**
- Unresolved threads (count and age)
- Days PR has been open
- Coherence: title ↔ description ↔ work items
- Change volume: number of files and lines touched

## Phase E — Report and Actions

**E.1 — Generate report:**
Build report using `assets/template-pr-review-report.md` and present in chat.

**E.2 — Determine verdict and present options:**

Verdict is derived automatically from analysis:

---

**Case 1 — PR aligned, no conflicts** (0 critical violations, 0 conflicts):
> ✅ **PR is aligned with standards and has no conflicts.**
> - 👍 **[A]** Approve — Add approval comment to PR
> - ❌ **[C]** Cancel review

**Case 2 — PR has conflicts** (mergeStatus indicates conflicts):
> ⚠️ **PR has the following conflicts:**
> [Conflict detail with explanation]
> - 🔧 **[R]** Resolve — Add resolution instructions as comment
> - 💬 **[G]** Add comment — Post findings as thread in PR
> - ❌ **[C]** Cancel review

**Case 3 — PR doesn't meet standards** (critical violations found):
> 🚫 **PR doesn't meet team-defined standards:**
> [List of violations with reference to violated standard]
> - 💬 **[G]** Add comment — Post findings as threads in PR
> - 👎 **[Z]** Reject — Rejection comment in PR
> - ❌ **[C]** Cancel review

**Mixed case** (conflicts + violations): Combine both and offer all applicable options: [R], [G], [Z], [C].

---

## Phase F — Execute Selected Action

**[A] Approve:**
1. Call `ado/repo_vote_pull_request` with:
   - `repositoryId`: repo ID
   - `pullRequestId`: PR ID
   - `vote`: `Approved`
2. Call `ado/repo_create_pull_request_thread` with:
   - `content`: `✅ **Code Review Approved** — PR analyzed against coding-standards.md. No violations or conflicts. [Brief summary]`
   - `status`: `Closed`
3. If prior pending record exists for this PR, remove from `pending_reviews.json`.
4. Confirm: `✅ PR #[PR_ID] approved. Vote registered + approval comment posted.`
5. No report file generated.

**[G] Add comment:**
1. For each relevant finding, call `ado/repo_create_pull_request_thread` with:
   - `content`: Finding description + standard reference + affected code snippet
   - `filePath`: Affected file path (from repo root, e.g. `/src/main/java/.../MyClass.java`)
   - `rightFileStartLine`: Finding start line number (right side of diff)
   - `rightFileEndLine`: Finding end line number
   - `rightFileStartOffset`: 1 (line start)
   - `rightFileEndOffset`: length of last flagged line
   - `status`: `Active`
   
   > **Lines must be taken from `git diff` output (Phase B.4). Headers `@@ -X,Y +Z,W @@` indicate right-side lines (`+Z`). Only anchor on lines showing `+` in the diff — never on unmodified code.**

2. If a finding has no specific file/line (e.g. branch convention, commit message), create thread without `filePath` — appears as general PR comment.
3. Confirm: `💬 [X] threads created in PR #[PR_ID] (Y anchored in code, Z general).`
4. Ask user:
   > **🤷 Generate review report as file?**
   > - 📄 **[S]** Yes, save to `[Author Review Path]/review_PR_[PR_ID]_[timestamp].md`
   > - ❌ **[N]** No, chat only
5. If [S] accepted: generate file using `assets/template-pr-review-report.md`.

**[Z] Reject:**
> ⚠️ **Confirmation required:** Are you sure you want to post rejection on the PR?
> - ✅ **[S]** Yes, reject
> - ❌ **[N]** No, back to options

If confirmed:
1. Call `ado/repo_vote_pull_request` with:
   - `repositoryId`: repo ID
   - `pullRequestId`: PR ID
   - `vote`: `Rejected`
2. Call `ado/repo_create_pull_request_thread` with:
   - `content`: `🚫 **Code Review — Not Approved** — Violations found: [list]. See coding-standards.md for reference.`
   - `status`: `Active`
3. Confirm: `🚫 PR #[PR_ID] rejected. Rejection vote registered + comment posted.`
4. No report file generated.

**[R] Resolve (conflicts):**
1. Call `ado/repo_create_pull_request_thread` with resolution instructions:
   - `content`: `⚠️ **Merge conflicts detected.** Manual rebase or merge of [targetRefName] into [sourceRefName] required.` + conflicted file detail if available.
   - `status`: `Active`

**[C] Cancel review:**
1. Record in `[Reviewer Pending Path]/pending_reviews.json`:
   ```json
   {
     "pr_id": "[PR_ID]",
     "titulo": "[PR Title]",
     "pendiente_por": "[Reason: conflicts/violations/detail]",
     "responsable": "[createdBy.displayName]",
     "responsable_email": "[createdBy.uniqueName]",
     "rama_origen": "[sourceRefName]",
     "rama_destino": "[targetRefName]",
     "fecha_revision": "[ISO timestamp]",
     "revisado_por": "[active user_email]"
   }
   ```
2. If file exists, append to array. If not, create array with this first record.
3. Confirm:
   > 📝 **Review cancelled and recorded as pending.** PR #[PR_ID] saved to `pending_reviews.json`.

## PENDIENTES-PR Command

Lists pending reviews for the **current reviewer** (`user_email`).

### Flow

1. Read `[Reviewer Pending Path]/pending_reviews.json`. If doesn't exist: `📭 No pending reviews registered.`
2. Present table:

| PR ID | Title | Pending Reason | Owner | Branch | Date |
|-------|-------|---------------|-------|--------|------|
| [ID]  | [Title] | [Summary] | [Author] | `[source]` → `[target]` | [date] |

3. Options:
> 📋 **Pending reviews loaded.**
> - 🔄 **[R]** Resume review of a PR (runs `REVISAR-PR`)
> - 🗑️ **[D]** Discard a pending item (remove from JSON)
> - ❌ **[N]** Nothing
