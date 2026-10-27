# PR Comment Resolver — Detailed Phase Reference

## Phase A — Resolve PR

Same resolution as `ado-pr-reviewer` Phase A:

1. **Parse input:** pure number → `pullRequestId`; ADO URL (`_git/` + `pullrequest/`) →
   extract `repositoryName` and `pullRequestId`.
2. Resolve `repositoryId` via `mcp__ado__repo_pull_request` (`action: list`) if only
   a numeric ID was given, or directly if the repo name came from a URL.
3. `mcp__ado__repo_pull_request` (`action: get`, `repositoryId`, `pullRequestId`) →
   get `sourceRefName`, `targetRefName`, author, status.
4. If the PR doesn't exist or isn't in the active project → inform the user and stop.

## Phase B — List and Select Threads

1. `mcp__ado__repo_pull_request_thread` (`action: list`, `repositoryId`, `pullRequestId`).
2. Filter to `status: Active` or `Pending`. Drop threads authored by service
   identities (build/policy bots) — keep only human-authored ones.
3. For each surviving thread, `mcp__ado__repo_pull_request_thread`
   (`action: list_comments`, `threadId`) to pull the **entire** comment history,
   not just the first comment — a later reply can redefine the ask.
4. Present a table:

   | # | File:Line | Author | Last comment (excerpt) | Age |
   |---|-----------|--------|-------------------------|-----|

5. Ask which to tackle now: comma-separated thread IDs, or `ALL`. This only
   selects which threads to attempt — it is not approval to write anything
   (see Phase C.5).

## Phase C — Per Selected Thread

Repeat for each thread chosen in Phase B:

1. **Working tree safety check:**
   - `git status` — if there are unrelated uncommitted changes, warn the user
     and ask before touching anything.
   - Confirm the checked-out branch matches the PR's `sourceRefName` (strip
     `refs/heads/`). Checkout/fetch it if needed, only after the status check
     above is clean.
2. Read the file at the line the thread is anchored to, from the local
   working tree (current state, not the diff).
3. **Propose a fix** that satisfies both:
   - what the reviewer is asking for (from the full thread history, Phase B.3)
   - the coding standard loaded earlier — cite the specific rule
4. **Apply the fix locally** (Edit tool). Touch only what the comment
   requires — no unrelated cleanup.
5. **Preview and confirm — mandatory for every thread, no exceptions:**

   > 🧵 Hilo #[id] — `[file]:[line]`
   > Comentario: "[excerpt]"
   > Regla aplicada: [standard rule reference]
   > Diff propuesto:
   > ```diff
   > [diff]
   > ```
   > - **[A]** Aplicar + Responder + Marcar Fixed
   > - **[W]** Responder y marcar WontFix (sin tocar código)
   > - **[E]** Dejar para que yo lo edite
   > - **[S]** Omitir este hilo

6. Execute the chosen action:
   - **[A]:** keep the local edit. `mcp__ado__repo_pull_request_thread_write`
     (`action: reply`, `threadId`, `content`: explanation + standard reference).
     Then (`action: update_status`, `threadId`, `status: Fixed`).
   - **[W]:** revert any local edit made for this thread.
     (`action: reply`, `content`: justification for not changing code).
     Then (`action: update_status`, `status: WontFix`).
   - **[E]:** revert any local edit. Leave the thread `Active`. Note it in the
     Phase D summary as "left for manual edit."
   - **[S]:** revert any local edit. No ADO write. Move to the next thread.

## Phase D — Final Summary (chat only, no file)

Present a table:

| Thread | Result | File | Note |
|--------|--------|------|------|

Then list every file modified locally and **not committed**, and remind the
user:

> ⚠️ Los cambios quedaron en tu working tree sin commitear. Revisa `git diff`,
> haz commit y push cuando estés listo.
