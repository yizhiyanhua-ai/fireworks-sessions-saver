#!/usr/bin/env python3
"""Lightweight heartbeat — updates last_active and records recently touched files.

Called automatically via PostToolUse hook. Designed to be fast and silent.
Does NOT create a full checkpoint; that's the AI's responsibility.

Usage: python heartbeat.py [working_dir]
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path.home() / ".claude" / "sessions"


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def workdir_hash(working_dir: str) -> str:
    return hashlib.md5(working_dir.encode()).hexdigest()[:8]


def get_modified_files(working_dir: str) -> "list[str]":
    """Return absolute paths of files modified in git working tree."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=working_dir, stderr=subprocess.DEVNULL
        ).decode().strip()
        files = [os.path.join(working_dir, f) for f in out.split("\n") if f]
        # Also include untracked files
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=working_dir, stderr=subprocess.DEVNULL
        ).decode().strip()
        files += [os.path.join(working_dir, f) for f in untracked.split("\n") if f]
        return files[:10]  # cap to avoid bloat
    except Exception:
        return []


def main():
    working_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
    ap = SESSIONS_DIR / f"active_{workdir_hash(working_dir)}.json"

    if not ap.exists():
        return  # no active session, nothing to do

    try:
        session = json.loads(ap.read_text())
    except Exception:
        return

    session["last_active"] = now_iso()

    # Merge recently modified files into the latest checkpoint's file list
    modified = get_modified_files(working_dir)
    if modified and session.get("checkpoints"):
        latest = session["checkpoints"][-1]
        existing_paths = {f["path"] for f in latest.get("files", [])}
        for fpath in modified:
            if fpath not in existing_paths:
                p = Path(fpath)
                mtime = None
                try:
                    mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    pass
                latest.setdefault("files", []).append({
                    "path": fpath,
                    "last_modified": mtime,
                    "role": "editing",
                    "note": ""
                })
        # Keep file list bounded
        latest["files"] = latest["files"][-20:]

    try:
        ap.write_text(json.dumps(session, indent=2, ensure_ascii=False))
    except Exception:
        pass  # silent failure — heartbeat must never break the user's workflow


if __name__ == "__main__":
    main()
