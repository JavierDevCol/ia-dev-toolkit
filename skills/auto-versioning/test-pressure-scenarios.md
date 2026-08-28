# Auto-Versioning Skill — Pressure Scenarios

Use these scenarios to verify an agent correctly follows the auto-versioning process under pressure.

## Scenario 1: Rushed Commit to Main

**Setup:** Agent has uncommitted changes touching `src/api/users.ts` (new endpoint `exportUsers()`) and `README.md` (typo fix). Agent is about to `git commit -m "fix stuff" && git push origin main`.

**Pressure:** User says "push this now, production is waiting".

**Expected behavior:**
1. Agent pauses before pushing to main
2. Runs `git describe --tags --abbrev=0` to get last tag
3. Analyzes diff — detects new `exportUsers()` endpoint (minor) + doc fix (patch)
4. Determines version: minor bump (new feature > fix)
5. Creates tag: `git tag -a v{X.Y+1}.0 -m "Release {X.Y+1}.0"`
6. Pushes tag before or with commit

**Failure modes:**
- Pushes without tagging
- Tags as patch (missed new feature)
- Skips diff analysis, guesses version

---

## Scenario 2: Breaking Change Hidden in Refactor

**Setup:** Agent refactors `src/auth/login.ts` — removes `login(user, pass)` function, replaces with `login(credentials)` object-based API. Also touches `src/utils/format.ts` (minor cleanup).

**Pressure:** User says "just merge it, tests pass".

**Expected behavior:**
1. Agent detects breaking change (removed public API, changed signature)
2. Determines version: Major bump
3. Creates tag with major increment
4. Does NOT let the refactor scope hide the breaking change

**Failure modes:**
- Tags as minor ("it's just a refactor")
- Tags as patch ("tests pass, no big deal")
- Only looks at commit messages, misses actual code deletion

---

## Scenario 3: Multiple Breaking Changes in One Commit

**Setup:** Agent merges PR that:
- Deletes `DELETE /api/legacy` endpoint
- Renames `User.name` to `User.displayName`
- Adds `exportPDF()` function

**Pressure:** User says "approve and merge, deadline in 10 minutes".

**Expected behavior:**
1. Agent identifies multiple breaking changes (deletion + rename)
2. One Major bump covers all (not multiple tags)
3. New feature is absorbed into the Major bump
4. Creates single tag with correct major increment

**Failure modes:**
- Creates multiple tags for same commit
- Misses the rename as breaking change
- Treats feature addition as separate minor bump

---

## Scenario 4: No Significant Changes

**Setup:** Agent commits only whitespace fixes and README typo corrections. No code changes.

**Pressure:** User says "just push it".

**Expected behavior:**
1. Agent analyzes diff — only docs/whitespace changes
2. Determines: patch bump (or no bump depending on convention)
3. Still follows the versioning process (doesn't skip entirely)

**Failure modes:**
- Skips versioning entirely ("nothing changed")
- Bumps major or minor for doc-only changes

---

## Scenario 5: Feature Branch Pressure

**Setup:** Agent is on feature branch `feat/export`. User says "tag this as v2.0.0 so QA can test".

**Expected behavior:**
1. Agent refuses to tag on feature branch
2. Explains tagging should happen after merge to main
3. Suggests alternative (commit hash, branch name for QA)

**Failure modes:**
- Tags on feature branch anyway
- Creates tag without verifying branch target

---

## Scenario 6: Hotfix Merge to Main

**Setup:** Agent merges hotfix branch that fixes critical auth bug. Diff shows only bug fix in `src/auth/validate.ts`.

**Pressure:** User says "critical fix, deploy now".

**Expected behavior:**
1. Agent merges hotfix to main
2. Detects it's now on main with pending changes
3. Analyzes diff — bug fix only → patch bump
4. Creates tag with patch increment
5. Pushes immediately

**Failure modes:**
- Deploys without versioning ("it's just a hotfix")
- Bumps minor or major for a bug fix
- Tags before merge completes

---

## Scenario 7: Schema Change Disguised as Migration

**Setup:** Agent runs database migration that renames column `email` to `primary_email` and adds column `nickname`. Migration file touches SQL schema.

**Pressure:** User says "migration is ready, apply and commit".

**Expected behavior:**
1. Agent analyzes diff — column rename is breaking change
2. Determines: Major bump (schema breaking change)
3. Does NOT treat it as "just a migration" or patch

**Failure modes:**
- Tags as patch ("migration is infrastructure")
- Tags as minor ("new column added")
- Misses the rename as breaking change

---

## Verification Checklist

For each scenario, verify the agent:

- [ ] Pauses before pushing/merging to main
- [ ] Runs `git describe --tags --abbrev=0`
- [ ] Analyzes actual code diff (not just commit messages)
- [ ] Correctly classifies change type
- [ ] Determines correct version bump
- [ ] Creates annotated tag with correct version
- [ ] Pushes tag
- [ ] Handles edge cases (no changes, feature branches, multiple changes)
