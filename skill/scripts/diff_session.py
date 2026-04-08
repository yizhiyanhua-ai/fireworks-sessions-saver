#!/usr/bin/env python3
"""Show a diff between two checkpoints in a session file.

Usage:
  python diff_session.py --session-file <path> [--from N] [--to M]

  N and M are 1-based checkpoint indices (default: last two checkpoints).
  Use --list to show all available checkpoints.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def time_ago(iso: str) -> str:
    try:
        delta = datetime.now() - datetime.fromisoformat(iso)
        if delta.days > 0:
            return f"{delta.days}d ago"
        h = delta.seconds // 3600
        if h > 0:
            return f"{h}h ago"
        m = delta.seconds // 60
        return f"{m}m ago" if m > 0 else "just now"
    except Exception:
        return iso


def diff_list(old: list, new: list) -> list[str]:
    old_set, new_set = set(old), set(new)
    lines = []
    for item in old_set - new_set:
        lines.append(f"  - {item}")
    for item in new_set - old_set:
        lines.append(f"  + {item}")
    return lines


def diff_files(old: list, new: list) -> list[str]:
    old_map = {f["path"]: f for f in old}
    new_map = {f["path"]: f for f in new}
    lines = []
    for path in set(old_map) - set(new_map):
        lines.append(f"  - {path}  [{old_map[path].get('role', '')}]")
    for path in set(new_map) - set(old_map):
        lines.append(f"  + {path}  [{new_map[path].get('role', '')}]")
    for path in set(old_map) & set(new_map):
        o, n = old_map[path], new_map[path]
        if o.get("role") != n.get("role"):
            lines.append(f"  ~ {path}  {o.get('role','')} → {n.get('role','')}")
        elif o.get("note") != n.get("note") and n.get("note"):
            lines.append(f"  ~ {path}  note: {n.get('note','')}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff two session checkpoints")
    parser.add_argument("--session-file", required=True)
    parser.add_argument("--from", dest="from_idx", type=int, default=None,
                        help="1-based index of the older checkpoint")
    parser.add_argument("--to", dest="to_idx", type=int, default=None,
                        help="1-based index of the newer checkpoint")
    parser.add_argument("--list", action="store_true", help="List all checkpoints")
    args = parser.parse_args()

    path = Path(args.session_file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    try:
        session = json.loads(path.read_text())
    except Exception as e:
        print(f"Failed to parse session file: {e}", file=sys.stderr)
        return 1

    checkpoints = session.get("checkpoints", [])
    if not checkpoints:
        print("No checkpoints found in this session.")
        return 0

    if args.list:
        print(f"Checkpoints in {path.name}:")
        for i, cp in enumerate(checkpoints, 1):
            print(f"  [{i}] {cp.get('timestamp', '?')}  —  {cp.get('summary', '(no summary)')[:60]}")
        return 0

    n = len(checkpoints)
    from_idx = args.from_idx if args.from_idx is not None else max(1, n - 1)
    to_idx   = args.to_idx   if args.to_idx   is not None else n

    if not (1 <= from_idx <= n) or not (1 <= to_idx <= n):
        print(f"Index out of range. Session has {n} checkpoint(s).", file=sys.stderr)
        return 1
    if from_idx == to_idx:
        print("--from and --to must be different checkpoints.", file=sys.stderr)
        return 1

    old_cp = checkpoints[from_idx - 1]
    new_cp = checkpoints[to_idx - 1]

    print("=" * 60)
    print(f"CHECKPOINT DIFF  [{from_idx}] → [{to_idx}]")
    print("=" * 60)
    print(f"From:  {old_cp.get('timestamp', '?')}  ({time_ago(old_cp.get('timestamp',''))})")
    print(f"To:    {new_cp.get('timestamp', '?')}  ({time_ago(new_cp.get('timestamp',''))})")
    print()

    changed = False

    # Task
    old_task = old_cp.get("current_task") or ""
    new_task = new_cp.get("current_task") or ""
    if old_task != new_task:
        changed = True
        print("── Task ──────────────────────────────────────────────")
        if old_task:
            print(f"  - {old_task}")
        if new_task:
            print(f"  + {new_task}")
        print()

    # Summary
    old_sum = old_cp.get("summary") or ""
    new_sum = new_cp.get("summary") or ""
    if old_sum != new_sum:
        changed = True
        print("── Summary ───────────────────────────────────────────")
        if old_sum:
            print(f"  - {old_sum}")
        if new_sum:
            print(f"  + {new_sum}")
        print()

    # Files
    file_lines = diff_files(old_cp.get("files", []), new_cp.get("files", []))
    if file_lines:
        changed = True
        print("── Files ─────────────────────────────────────────────")
        for line in file_lines:
            print(line)
        print()

    # Decisions
    dec_lines = diff_list(
        old_cp.get("key_decisions", []),
        new_cp.get("key_decisions", [])
    )
    if dec_lines:
        changed = True
        print("── Key Decisions ─────────────────────────────────────")
        for line in dec_lines:
            print(line)
        print()

    # Open questions
    q_lines = diff_list(
        old_cp.get("open_questions", []),
        new_cp.get("open_questions", [])
    )
    if q_lines:
        changed = True
        print("── Open Questions ────────────────────────────────────")
        for line in q_lines:
            print(line)
        print()

    # Git branch
    old_branch = old_cp.get("git_branch")
    new_branch = new_cp.get("git_branch")
    if old_branch != new_branch:
        changed = True
        print("── Git Branch ────────────────────────────────────────")
        print(f"  - {old_branch or '(none)'}")
        print(f"  + {new_branch or '(none)'}")
        print()

    if not changed:
        print("No differences found between the two checkpoints.")

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
