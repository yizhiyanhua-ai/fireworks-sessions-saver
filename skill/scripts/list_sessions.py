#!/usr/bin/env python3
"""List recoverable sessions for a working directory.

Usage: python list_sessions.py [working_dir]
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

SESSIONS_DIR = Path.home() / ".claude" / "sessions"
EXPIRY_DAYS = 7


def workdir_hash(working_dir: str) -> str:
    return hashlib.md5(working_dir.encode()).hexdigest()[:8]


def time_ago(dt: datetime) -> str:
    delta = datetime.now() - dt
    if delta.days > 0:
        return f"{delta.days} day(s) ago"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} hour(s) ago"
    minutes = delta.seconds // 60
    return f"{minutes} minute(s) ago" if minutes > 0 else "just now"


def load_session_summary(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text())
        if data.get("status") == "transferred":
            return None
        last_active = datetime.fromisoformat(data.get("last_active", data["start_time"]))
        if last_active < datetime.now() - timedelta(days=EXPIRY_DAYS):
            return None
        checkpoints = data.get("checkpoints", [])
        if not checkpoints:
            return None
        latest = checkpoints[-1]
        return {
            "file": str(path),
            "tool": data.get("tool", "unknown"),
            "last_active": last_active,
            "summary": latest.get("summary", "No summary"),
            "current_task": latest.get("current_task", ""),
            "open_questions": latest.get("open_questions", []),
            "files": [f["path"] for f in latest.get("files", [])],
            "checkpoint_count": len(checkpoints),
        }
    except Exception:
        return None


def main():
    working_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    wh = workdir_hash(working_dir)

    if not SESSIONS_DIR.exists():
        print("No previous sessions found.")
        return

    sessions = []

    # Check archive files for this working dir
    for f in SESSIONS_DIR.glob(f"archive_{wh}_*.json"):
        s = load_session_summary(f)
        if s:
            sessions.append(s)

    # Check active file — may be from a crashed previous session
    active = SESSIONS_DIR / f"active_{wh}.json"
    s = load_session_summary(active)
    if s:
        sessions.append(s)

    sessions.sort(key=lambda x: x["last_active"], reverse=True)

    if not sessions:
        print("No previous sessions found for this project.")
        return

    print(f"Found {len(sessions)} previous session(s) for: {working_dir}\n")
    for i, s in enumerate(sessions, 1):
        ago = time_ago(s["last_active"])
        print(f"[{i}] {s['last_active'].strftime('%Y-%m-%d %H:%M')} ({ago}) — {s['tool']}")
        print(f"    Summary:  {s['summary']}")
        if s["current_task"]:
            print(f"    Task:     {s['current_task']}")
        if s["files"]:
            print(f"    Files:    {', '.join(s['files'][:3])}")
        if s["open_questions"]:
            print(f"    Open:     {s['open_questions'][0]}")
        print(f"    File:     {s['file']}")
        print()


if __name__ == "__main__":
    main()
