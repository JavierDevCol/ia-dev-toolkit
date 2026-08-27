#!/usr/bin/env python3
"""Git Documentation Sync — selective commit/push for documentation repos.

Usage:
  python3 scripts/sync_logic.py inventory --file inventory.json
  python3 scripts/sync_logic.py status --path /repo --branches main,develop
  python3 scripts/sync_logic.py sync --path /repo --files "a.md,b.md" --message "docs: update"
"""

import argparse
import json
import subprocess
import sys


def run_git(args, cwd):
    """Run a git command in the given directory. Returns stdout on success."""
    result = subprocess.run(
        args, capture_output=True, text=True, cwd=cwd
    )
    if result.returncode != 0:
        error_msg = result.stderr.strip() or f"git command failed: {' '.join(args)}"
        print(json.dumps({"error": error_msg}), file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout


def cmd_inventory(args):
    """List registered repositories from the shared memory_skill.json."""
    try:
        with open(args.file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(json.dumps({"error": f"Memory file not found: {args.file}"}))
        sys.exit(1)

    section = data.get(args.skill_key, {})
    repos = section.get("memory", {}).get("inventory", [])
    settings = section.get("config", {})
    print(json.dumps({
        "repos": repos,
        "required_branches": settings.get("required_branches", []),
        "count": len(repos),
    }, indent=2))


def cmd_status(args):
    """Show categorized git status as JSON."""
    # Validate branch
    current_branch = run_git(
        ["git", "branch", "--show-current"], cwd=args.path
    ).strip()

    allowed = [b.strip() for b in args.branches.split(",")] if args.branches else []
    if allowed and current_branch not in allowed:
        print(json.dumps({
            "error": f"Branch '{current_branch}' is not allowed. Allowed: {allowed}"
        }))
        sys.exit(1)

    raw = run_git(["git", "status", "--short"], cwd=args.path)
    files = []
    for line in raw.strip().split("\n"):
        if not line:
            continue
        code = line[:2].strip()
        filepath = line[3:]
        if code == "??":
            category = "NEW"
        elif code == "D":
            category = "DELETED"
        else:
            category = "MODIFIED"
        files.append({"category": category, "file": filepath})

    print(json.dumps({
        "branch": current_branch,
        "files": files,
        "count": len(files),
    }, indent=2))


def cmd_sync(args):
    """Stage selected files, commit, and push."""
    file_list = [f.strip() for f in args.files.split(",") if f.strip()]
    if not file_list:
        print(json.dumps({"error": "No files specified. Use --files 'a.md,b.md'"}))
        sys.exit(1)

    for f in file_list:
        run_git(["git", "add", f], cwd=args.path)

    run_git(["git", "commit", "-m", args.message], cwd=args.path)

    branch = run_git(
        ["git", "branch", "--show-current"], cwd=args.path
    ).strip()
    run_git(["git", "push", "origin", branch], cwd=args.path)

    print(json.dumps({
        "status": "ok",
        "branch": branch,
        "files_pushed": file_list,
        "message": args.message,
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Git Documentation Sync — selective commit/push for doc repos."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # inventory
    p_inv = subparsers.add_parser("inventory", help="List repos from shared memory file")
    p_inv.add_argument("--file", required=True, help="Path to memory_skill.json")
    p_inv.add_argument("--skill-key", default="git-doc-sync",
                       help="Skill section key inside memory_skill.json")

    # status
    p_st = subparsers.add_parser("status", help="Show categorized git status")
    p_st.add_argument("--path", required=True, help="Path to the git repository")
    p_st.add_argument("--branches", default="", help="Comma-separated allowed branches")

    # sync
    p_sync = subparsers.add_parser("sync", help="Stage, commit, and push selected files")
    p_sync.add_argument("--path", required=True, help="Path to the git repository")
    p_sync.add_argument("--files", required=True, help="Comma-separated files to stage")
    p_sync.add_argument("--message", required=True, help="Commit message")

    args = parser.parse_args()

    commands = {
        "inventory": cmd_inventory,
        "status": cmd_status,
        "sync": cmd_sync,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()