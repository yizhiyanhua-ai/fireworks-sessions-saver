#!/usr/bin/env python3
"""Print a structured context summary from a session archive file.

Usage: python restore_session.py --session-file <path>
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def time_ago(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        delta = datetime.now() - dt
        if delta.days > 0:
            return f"{delta.days} day(s) ago"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours} hour(s) ago"
        minutes = delta.seconds // 60
        return f"{minutes} minute(s) ago" if minutes > 0 else "just now"
    except Exception:
        return iso


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-file", required=True)
    args = parser.parse_args()

    path = Path(args.session_file)
    if not path.exists():
        print(f"Session file not found: {path}")
        return 1

    data = json.loads(path.read_text())
    checkpoints = data.get("checkpoints", [])

    print("=" * 60)
    print("SESSION CONTEXT RESTORE")
    print("=" * 60)
    print(f"Tool:         {data.get('tool', 'unknown')}")
    print(f"Working dir:  {data.get('working_dir', '')}")
    print(f"Session ID:   {data.get('session_id', '')}")
    print(f"Started:      {data.get('start_time', '')} ({time_ago(data.get('start_time', ''))})")
    print(f"Last active:  {data.get('last_active', '')} ({time_ago(data.get('last_active', ''))})")
    print(f"Checkpoints:  {len(checkpoints)}")
    print()

    if not checkpoints:
        print("No checkpoints recorded.")
        return 0

    # Most recent checkpoint is the primary restore point
    latest = checkpoints[-1]
    print("─" * 60)
    print("LATEST STATE")
    print("─" * 60)

    if latest.get("summary"):
        print(f"Summary:      {latest['summary']}")
    if latest.get("current_task"):
        print(f"Current task: {latest['current_task']}")
    if latest.get("git_branch"):
        print(f"Git branch:   {latest['git_branch']}")

    commits = latest.get("git_recent_commits", [])
    if commits:
        print("Recent commits:")
        for c in commits:
            print(f"  {c}")

    files = latest.get("files", [])
    if files:
        print("Files in context:")
        for f in files:
            role = f.get("role", "")
            note = f.get("note", "")
            mtime = f.get("last_modified", "")
            exists = Path(f["path"]).exists()
            status = "" if exists else " [MISSING]"
            line = f"  [{role}] {f['path']}{status}"
            if mtime:
                line += f"  (modified {mtime})"
            if note:
                line += f"\n         → {note}"
            print(line)

    decisions = latest.get("key_decisions", [])
    if decisions:
        print("Key decisions:")
        for d in decisions:
            print(f"  • {d}")

    questions = latest.get("open_questions", [])
    if questions:
        print("Open questions / blockers:")
        for q in questions:
            print(f"  ? {q}")

    commands = latest.get("recent_commands", [])
    if commands:
        print("Recent commands:")
        for c in commands:
            print(f"  $ {c}")

    log_refs = latest.get("log_refs", {})
    cc_log = log_refs.get("claude_code")
    codex_log = log_refs.get("codex")
    if cc_log or codex_log:
        print("Log files (for deeper context):")
        if cc_log:
            exists = Path(cc_log).exists()
            print(f"  Claude Code: {cc_log}{'' if exists else ' [NOT FOUND]'}")
        if codex_log:
            exists = Path(codex_log).exists()
            print(f"  Codex:       {codex_log}{'' if exists else ' [NOT FOUND]'}")

    # Show older checkpoints as a timeline if there are multiple
    if len(checkpoints) > 1:
        print()
        print("─" * 60)
        print("CHECKPOINT HISTORY")
        print("─" * 60)
        for i, cp in enumerate(reversed(checkpoints[:-1]), 1):
            ts = cp.get("timestamp", "")
            summary = cp.get("summary", "—")
            task = cp.get("current_task", "")
            print(f"  [{i} back] {ts}  {summary}")
            if task and task != summary:
                print(f"           task: {task}")

    print()
    print("=" * 60)
    print("Restore complete. Use the above context to resume work.")
    print(f"Session file: {path}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
