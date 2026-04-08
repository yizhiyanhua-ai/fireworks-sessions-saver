# Log File Locations for Claude Code and Codex

When restoring a session, these log files can provide supplementary context beyond what was manually checkpointed.

> **Important**: Only store file *paths* in session files — never copy log content. Logs can be large and change frequently.

---

## Claude Code

### Project Conversation Logs

Claude Code stores per-project conversation history in:
```
~/.claude/projects/{project_dir_encoded}/
```

The directory name is derived from the absolute working directory path (slashes replaced with hyphens or similar encoding). To find the right project directory:

```bash
# List all project dirs sorted by modification time
ls -lt ~/.claude/projects/ | head -20

# Or search for a dir that matches your project name
ls ~/.claude/projects/ | grep <project_name_fragment>
```

Inside each project directory, look for:
- `*.jsonl` — conversation logs (one entry per line, JSON format)
- `todos.json` — saved todo lists

Each JSONL line contains a message object with `role`, `content`, and tool use records.

### Global Files

| Path | Contents |
|------|----------|
| `~/.claude/settings.json` | Global settings, hooks config |
| `~/.claude/settings.local.json` | Local overrides |
| `~/.claude/todos/` | Global todo lists |
| `~/.claude/skills/` | Installed skills |
| `~/.claude/CLAUDE.md` | Global instructions |

### Finding the Most Recent Log

```python
import os
from pathlib import Path

projects_dir = Path.home() / ".claude" / "projects"
if projects_dir.exists():
    # Find most recently modified project dir
    project_dirs = sorted(
        projects_dir.iterdir(),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    for pd in project_dirs[:3]:
        logs = sorted(pd.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
        if logs:
            print(f"Recent log: {logs[0]}")
            break
```

---

## Codex (OpenAI CLI)

Codex CLI stores data in:
```
~/.codex/
```

Common subdirectories (may vary by version):
| Path | Contents |
|------|----------|
| `~/.codex/history` | Command/conversation history |
| `~/.codex/logs/` | Session logs |
| `~/.codex/config.json` | Configuration |

To discover what's available:
```bash
ls -la ~/.codex/
find ~/.codex/ -name "*.json" -o -name "*.jsonl" | sort
```

### Finding Recent Codex Logs

```python
from pathlib import Path

codex_dir = Path.home() / ".codex"
if codex_dir.exists():
    log_files = sorted(
        list(codex_dir.rglob("*.json")) + list(codex_dir.rglob("*.jsonl")),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )
    for f in log_files[:5]:
        print(f)
```

---

## Using Log References in Checkpoints

When saving a checkpoint, the `save_session.py` script automatically discovers and records log file paths in the `log_refs` field:

```json
"log_refs": {
  "claude_code": "/Users/user/.claude/projects/my-project-abc123/2026-04-08.jsonl",
  "codex": null
}
```

When restoring, these paths let you (or the AI) quickly locate the full conversation history for deeper context recovery.
