---
name: auto-versioning
description: Use when pushing, merging a PR, or committing to main branch. Self-triggers on semantic versioning needs. Triggers on "version", "tag", "release", "semver", "git tag", "version bump", "push to main", "merge to main"
ready: true
---

# Auto-Versioning

## Overview

Determines the next semantic version by analyzing code diffs between the last tag and pending changes. Follows SemVer rules: breaking changes → Major, new features → Minor, fixes/docs → Patch.

## When to Use

- Committing to main branch
- Merging a PR to main
- Pushing changes to main

**Flowchart:**

```dot
digraph version_flowchart {
    "Commit/merge/push to main?" [shape=diamond];
    "Get last tag" [shape=box];
    "Analyze diff" [shape=box];
    "Breaking changes?" [shape=diamond];
    "New features?" [shape=diamond];
    "Increment Major" [shape=box];
    "Increment Minor" [shape=box];
    "Increment Patch" [shape=box];
    "Create and push tag" [shape=box];
    "No significant changes" [shape=box];

    "Commit/merge/push to main?" -> "Get last tag" [label="yes"];
    "Commit/merge/push to main?" -> "Skip" [label="no"];
    "Get last tag" -> "Analyze diff";
    "Analyze diff" -> "Breaking changes?";
    "Breaking changes?" -> "Increment Major" [label="yes"];
    "Breaking changes?" -> "New features?" [label="no"];
    "New features?" -> "Increment Minor" [label="yes"];
    "New features?" -> "Increment Patch" [label="no"];
    "Increment Major" -> "Create and push tag";
    "Increment Minor" -> "Create and push tag";
    "Increment Patch" -> "Create and push tag";
    "Create and push tag" -> "Done";
    "No significant changes" -> "Done";
    "Skip" -> "Done";
    "Done" [shape=doublecircle];
}
```

## When NOT to Use

- Committing to feature branches (use manual versioning or skip)
- Hotfix branches (determine version after merge to main)
- Initial project setup (start at v0.1.0 manually)

## Implementation

1. Detectar si el push/merge es hacia `main`:
   - Si el agente acaba de hacer `git push origin main` → **activar**
   - Si el agente acaba de mergear PR a `main` → **activar**
   - Si NO → **detenerse** (no ejecutar versioning)
2. Obtener último tag: `git describe --tags --abbrev=0`
3. Analizar diff: `git diff {last_tag}...HEAD`
4. Clasificar cambios: Major / Minor / Patch (ver Diff Analysis Triggers)
5. Calcular versión siguiente
6. Crear tag: `git tag -a v{version} -m "Release {version}"`
7. Push tag: `git push origin v{version}`

## Quick Reference

| Change Type | Example | Bump |
|---|---|---|
| API removal, signature change | Remove `getUser()` endpoint | Major |
| New feature, new endpoint | Add `exportCSV()` function | Minor |
| Bug fix, docs, refactor | Fix typo, update README | Patch |

## Diff Analysis Triggers

**Major:** Removed public APIs, changed signatures, deleted endpoints, modified schema/config format

**Minor:** Added functions/classes, new endpoints, new features, new config options

**Patch:** Bug fixes, docs, refactoring, performance, tests

## Commands

```bash
# Get last tag
git describe --tags --abbrev=0

# Get diff
git diff {last_tag}...HEAD

# Create tag
git tag -a v{version} -m "Release {version}" && git push origin v{version}
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Analyzing commit messages only | Always inspect actual code diffs |
| Missing removed APIs | Check for deletions and signature changes |
| Forgetting to push tags | Push immediately after creation |
| Tagging feature branches | Only tag on main branch |
