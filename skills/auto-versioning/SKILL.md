---
name: auto-versioning
description: Use when committing, merging, or creating PRs to main branch to automatically determine and create the next version tag based on diff analysis
ready: true
---

# Auto-Versioning

## Overview

Determines the next semantic version (SemVer) by analyzing code diffs between the last tag and the changes being pushed to main. The agent follows this process automatically.

## When to Use

- Before committing to main branch
- Before merging a PR to main
- Before pushing to main
- After receiving a PR approval

## Process Flowchart

```
Start
    ↓
Get last tag from GitHub API or git
    ↓
Get diff between last tag and HEAD (or pending changes)
    ↓
Analyze diff for:
  - Breaking changes → Major
  - New features → Minor
  - Bug fixes → Patch
    ↓
Calculate new version
    ↓
Create tag automatically
    ↓
Push tag to origin
```

## Versioning Rules (SemVer)

| Diff Analysis | Version | Example |
|---|---|---|
| Breaking changes (API removal, signature change) | Major | `v0.2.1` → `v1.0.0` |
| New features (functions, modules, capabilities) | Minor | `v0.2.1` → `v0.3.0` |
| Bug fixes, docs, refactoring | Patch | `v0.2.1` → `v0.2.2` |
| No significant changes | No tag | — |

## Diff Analysis Rules

### Major Version Triggers

- Removed public functions/classes
- Changed function signatures
- Deleted API endpoints
- Modified database schema
- Changed configuration format

### Minor Version Triggers

- Added new functions/classes
- Added new API endpoints
- Added new features
- Added new configuration options
- Added new files

### Patch Version Triggers

- Bug fixes
- Documentation updates
- Code refactoring
- Performance improvements
- Test additions

## Commands to Execute

### 1. Get Last Tag

```bash
# From GitHub API (preferred)
curl -s https://api.github.com/repos/{owner}/{repo}/tags | jq -r '.[0].name'

# From git
git describe --tags --abbrev=0
```

### 2. Get Diff

```bash
# Between last tag and HEAD
git diff {last_tag}...HEAD

# For pending changes (not yet committed)
git diff HEAD
```

### 3. Analyze Diff

Look for:
- Lines removed (`-`) that define public APIs
- Lines added (`+`) that define new functions/classes
- Lines removed (`-`) that fix bugs
- Lines added (`+`) that add features

### 4. Create Tag

```bash
# Create annotated tag
git tag -a v{version} -m "Release {version}"

# Push tag
git push origin v{version}
```

## Agent Execution

When the agent detects it's about to commit/merge/push to main:

1. **Run the analysis** using the commands above
2. **Determine version** based on diff content
3. **Create tag** with the new version
4. **Push tag** to origin
5. **Report** what was done

## Example Output

```
📊 Diff analysis:
   - Breaking changes: 0
   - New features: 2
   - Bug fixes: 1

🏷️  Creating tag: v0.3.0
✅ Tag v0.3.0 created and pushed
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Relying on commit titles | Always analyze actual diffs |
| Forgetting breaking changes | Check for removed/modified APIs |
| Overlooking minor additions | Scan for new functions/classes |
| Not pushing tags | Always push tags after creating |
