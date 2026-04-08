#!/usr/bin/env python3
"""Multi-project session dashboard — show all active sessions across all directories.

Usage: python dashboard.py [--all] [--json]

  --all   Include sessions that are expired (> 7 days) but not yet deleted
  --json  Output raw JSON instead of formatted table
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SESSIONS_DIR = Path.home() / ".claude" / "sessions"
EXPIRY_DAYS = 7


def time_ago(dt: datetime) -> str:
    delta = datetime.now() - dt
    if delta.days > 0:
        return f"{delta.days}d ago"
    h = delta.seconds // 3600
    if h > 0:
        return f"{h}h ago"
    m = delta.seconds // 60
    return f"{m}m ago" if m > 0 else "just now"


def load_all_sessions(include_expired: bool = False) -> list:
    if not SESSIONS_DIR.exists():
        return []

    sessions = []
    cutoff = datetime.now() - timedelta(days=EXPIRY_DAYS)

    for f in sorted(SESSIONS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue

        if data.get("status") == "transferred":
            continue

        last_active_str = data.get("last_active", "")
        try:
            last_active = datetime.fromisoformat(last_active_str)
        except Exception:
            continue

        expired = last_active < cutoff
        if expired and not include_expired:
            continue

        checkpoints = data.get("checkpoints", [])
        latest = checkpoints[-1] if checkpoints else {}

        sessions.append({
            "file": str(f),
            "session_id": data.get("session_id", "?"),
            "tool": data.get("tool", "unknown"),
            "working_dir": data.get("working_dir", "?"),
            "start_time": data.get("start_time", "?"),
            "last_active": last_active,
            "last_active_str": last_active_str,
            "status": "expired" if expired else data.get("status", "active"),
            "checkpoint_count": len(checkpoints),
            "summary": latest.get("summary", ""),
            "current_task": latest.get("current_task", ""),
            "git_branch": latest.get("git_branch", ""),
            "file_count": len(latest.get("files", [])),
        })

    sessions.sort(key=lambda s: s["last_active"], reverse=True)
    return sessions


def print_dashboard(sessions: list) -> None:
    if not sessions:
        print("No active sessions found.")
        print(f"Sessions are stored in: {SESSIONS_DIR}")
        return

    active   = [s for s in sessions if s["status"] == "active"]
    expired  = [s for s in sessions if s["status"] == "expired"]

    print("=" * 70)
    print(f"  SESSION DASHBOARD  —  {len(sessions)} session(s) found")
    print("=" * 70)

    if active:
        print(f"\n  ACTIVE  ({len(active)})\n")
        for i, s in enumerate(active, 1):
            ago = time_ago(s["last_active"])
            branch = f"  [{s['git_branch']}]" if s["git_branch"] else ""
            print(f"  [{i}] {s['last_active'].strftime('%Y-%m-%d %H:%M')} ({ago})  —  {s['tool']}{branch}")
            print(f"      Dir:   {s['working_dir']}")
            if s["summary"]:
                print(f"      Last:  {s['summary'][:60]}")
            if s["current_task"]:
                print(f"      Task:  {s['current_task'][:60]}")
            print(f"      CPs:   {s['checkpoint_count']}  ·  Files: {s['file_count']}")
            print(f"      File:  {s['file']}")
            print()

    if expired:
        print(f"  EXPIRED  ({len(expired)})  —  older than {EXPIRY_DAYS} days\n")
        for s in expired:
            ago = time_ago(s["last_active"])
            print(f"  · {s['last_active'].strftime('%Y-%m-%d')} ({ago})  {s['working_dir']}")
        print()

    print("=" * 70)
    print(f"  Storage: {SESSIONS_DIR}")
    print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-project session dashboard")
    parser.add_argument("--all", action="store_true", help="Include expired sessions")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    sessions = load_all_sessions(include_expired=args.all)

    if args.json:
        output = [
            {k: v for k, v in s.items() if k != "last_active"}
            for s in sessions
        ]
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0

    print_dashboard(sessions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
