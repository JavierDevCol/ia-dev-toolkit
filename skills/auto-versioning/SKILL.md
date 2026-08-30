---
name: auto-versioning
description: Use it before committing to the main branch to automatically determine and create the next version tag based on a diff analysis.
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
