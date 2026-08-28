---
name: auto-versioning
description: Use when committing, merging, or creating PRs to main branch to automatically determine and create the next version tag based on diff analysis
ready: true
---

# Auto-Versioning

## Overview

Automatically determines the next semantic version (SemVer) by analyzing code diffs, not commit titles. Validates actual changes in the codebase to suggest accurate versioning.

## When to Use

- Before merging to main branch
- When creating release tags
- After PR approval
- When preparing for deployment

## Versioning Rules (SemVer)

| Diff Analysis | Version | Example |
|---|---|---|
| Breaking changes (API removal, signature change) | Major | `v0.2.1` → `v1.0.0` |
| New features (functions, modules, capabilities) | Minor | `v0.2.1` → `v0.3.0` |
| Bug fixes, docs, refactoring | Patch | `v0.2.1` → `v0.2.2` |
| No significant changes | No tag | — |

## Flowchart

```
Start
    ↓
Get last tag from GitHub API
    ↓
Get diff between last tag and HEAD
    ↓
Analyze diff for:
  - Breaking changes (Major)
  - New features (Minor)
  - Bug fixes (Patch)
    ↓
Calculate new version
    ↓
Show to user + ask confirmation
    ↓
User confirms?
    ├─ YES → Create tag and push
    └─ NO → Ask which version to use
```

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

## Usage

### Interactive Mode

```bash
# Analyze diff and suggest version
python scripts/analyze-diff.py

# Or via diat CLI
diat --analyze-version
```

### Programmatic Usage

```python
from scripts.analyze_diff import analyze_diff, calculate_version

# Analyze diff
changes = analyze_diff("main")

# Calculate next version
new_version = calculate_version(changes)

# Show confirmation
print(f"Suggested: v{new_version}")
```

## Confirmation Format

```
╔═══════════════════════════════════════════════════════════════╗
║                    AUTO-VERSIONING                            ║
╚═══════════════════════════════════════════════════════════════╝

  📍 Last tag: v0.2.1
  📊 Diff analysis:
     - Breaking changes: 1 (function signature changed)
     - New features: 2
     - Bug fixes: 3

  🏷️  Suggested version: v1.0.0 (Major)

  Create tag v1.0.0? (s/N):
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Relying on commit titles | Always analyze actual diffs |
| Forgetting breaking changes | Check for removed/modified APIs |
| Overlooking minor additions | Scan for new functions/classes |

## Script Output

The `analyze-diff.py` script returns:

```json
{
  "last_tag": "v0.2.1",
  "changes": {
    "major": 1,
    "minor": 2,
    "patch": 3
  },
  "suggested_version": "1.0.0",
  "reason": "Breaking change detected"
}
```
