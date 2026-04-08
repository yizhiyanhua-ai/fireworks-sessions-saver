#!/usr/bin/env python3
"""Save or update a session checkpoint.

Actions:
  init        Create a new active session (archives existing one if it has checkpoints)
  checkpoint  Add a checkpoint to the active session
  cleanup     Delete an archive file after successful transfer
"""

import argparse
import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path.home() / ".claude" / "sessions"
MAX_CHECKPOINTS = 10


def workdir_hash(working_dir: str) -> str:
    return hashlib.md5(working_dir.encode()).hexdigest()[:8]


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def active_path(working_dir: str) -> Path:
    return SESSIONS_DIR / f"active_{workdir_hash(working_dir)}.json"


def get_git_info(working_dir: str) -> dict:
    info = {"branch": None, "recent_commits": []}
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=working_dir, stderr=subprocess.DEVNULL
        ).decode().strip()
        info["branch"] = branch or None

        commits = subprocess.check_output(
            ["git", "log", "--oneline", "-5"],
            cwd=working_dir, stderr=subprocess.DEVNULL
        ).decode().strip()
        info["recent_commits"] = [c for c in commits.split("\n") if c]
    except Exception:
        pass
    return info


def get_log_refs(tool: str) -> dict:
    refs = {"claude_code": None, "codex": None}  # type: dict

    if tool in ("claude-code", "claude"):
        projects_dir = Path.home() / ".claude" / "projects"
        if projects_dir.exists():
            all_logs = sorted(
                projects_dir.rglob("*.jsonl"),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            if all_logs:
                refs["claude_code"] = str(all_logs[0])

    if tool == "codex":
        codex_dir = Path.home() / ".codex"
        if codex_dir.exists():
            all_logs = sorted(
                list(codex_dir.rglob("*.json")) + list(codex_dir.rglob("*.jsonl")),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            if all_logs:
                refs["codex"] = str(all_logs[0])

    return refs


def parse_files(files_str: str) -> list:
    """Parse 'path:role,path:role' into file ref objects."""
    result = []
    if not files_str:
        return result
    for entry in files_str.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            path, role = entry.rsplit(":", 1)
        else:
            path, role = entry, "reference"
        p = Path(path.strip())
        mtime = None
        if p.exists():
            mtime = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S")
        result.append({
            "path": str(p),
            "last_modified": mtime,
            "role": role.strip(),
            "note": ""
        })
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-dir", required=True)
    parser.add_argument("--tool", default="claude-code")
    parser.add_argument("--action", choices=["init", "checkpoint", "cleanup"], required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument("--current-task", default="")
    parser.add_argument("--files", default="",
                        help="Comma-separated 'path:role' pairs, e.g. src/auth.ts:editing,README.md:reference")
    parser.add_argument("--decisions", default="", help="Semicolon-separated key decisions")
    parser.add_argument("--open-questions", default="", help="Semicolon-separated open questions")
    parser.add_argument("--commands", default="", help="Semicolon-separated recent commands")
    parser.add_argument("--archive-file", default="", help="Archive file to delete (for cleanup action)")
    args = parser.parse_args()

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    working_dir = os.path.abspath(args.working_dir)

    if args.action == "init":
        ap = active_path(working_dir)
        if ap.exists():
            existing = json.loads(ap.read_text())
            if existing.get("checkpoints"):
                arch = SESSIONS_DIR / f"archive_{workdir_hash(working_dir)}_{now_ts()}.json"
                ap.rename(arch)
                print(f"Archived previous session: {arch.name}")

        session = {
            "session_id": uuid.uuid4().hex[:8],
            "tool": args.tool,
            "working_dir": working_dir,
            "start_time": now_iso(),
            "last_active": now_iso(),
            "status": "active",
            "checkpoints": []
        }
        ap.write_text(json.dumps(session, indent=2, ensure_ascii=False))
        print(f"Session initialized: {ap}")

    elif args.action == "checkpoint":
        ap = active_path(working_dir)
        if not ap.exists():
            print("No active session found. Run --action init first.")
            return

        session = json.loads(ap.read_text())
        git = get_git_info(working_dir)
        log_refs = get_log_refs(args.tool)

        checkpoint = {
            "timestamp": now_iso(),
            "summary": args.summary,
            "current_task": args.current_task,
            "git_branch": git["branch"],
            "git_recent_commits": git["recent_commits"],
            "files": parse_files(args.files),
            "key_decisions": [d.strip() for d in args.decisions.split(";") if d.strip()],
            "open_questions": [q.strip() for q in args.open_questions.split(";") if q.strip()],
            "recent_commands": [c.strip() for c in args.commands.split(";") if c.strip()],
            "log_refs": log_refs
        }

        checkpoints = session.get("checkpoints", [])
        checkpoints.append(checkpoint)
        session["checkpoints"] = checkpoints[-MAX_CHECKPOINTS:]
        session["last_active"] = now_iso()

        ap.write_text(json.dumps(session, indent=2, ensure_ascii=False))
        print(f"Checkpoint saved ({len(session['checkpoints'])}/{MAX_CHECKPOINTS})")

    elif args.action == "cleanup":
        target = Path(args.archive_file) if args.archive_file else None
        if target and target.exists():
            target.unlink()
            print(f"Deleted transferred session: {target.name}")
        else:
            print("No archive file specified or file not found.")


if __name__ == "__main__":
    main()
