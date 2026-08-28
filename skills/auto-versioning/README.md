# Auto-Versioning Skill

Automatically determines the next semantic version tag by analyzing code diffs between the last tag and pending changes. Follows SemVer rules: breaking changes → Major, new features → Minor, fixes/docs → Patch.

## When It Triggers

- Committing, merging, or pushing to main branch
- Creating PRs targeting main

## How It Works

1. Detects action targets main branch
2. Gets last tag via `git describe --tags --abbrev=0`
3. Analyzes diff for breaking changes, features, or fixes
4. Determines correct version bump (Major/Minor/Patch)
5. Creates and pushes annotated tag

## Quick Example

```bash
# Before commit to main:
# Agent detects: new endpoint added, no breaking changes
# Agent runs:
git tag -a v1.2.0 -m "Release 1.2.0" && git push origin v1.2.0
```

## Diff Analysis Triggers

| Change Type | Bump |
|---|---|
| API removal, signature change, schema change | Major |
| New function, new endpoint, new config option | Minor |
| Bug fix, docs, refactoring, performance | Patch |
