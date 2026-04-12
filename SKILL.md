---
name: fireworks-sessions-saver
description: Session state persistence and recovery for Claude Code. TRIGGER when user asks about session persistence, context recovery, save progress, restore session, checkpoint, crash recovery, session dashboard, or wants to install fireworks-sessions-saver.
---

# fireworks-sessions-saver

Never lose your coding session context again. Auto-persists and restores session state for Claude Code.

## What It Does

Network timeouts, crashes, and accidental window closures kill your session context. `fireworks-sessions-saver` automatically tracks what you're working on and makes it instantly recoverable.

1. **Auto-tracking** — heartbeat hook updates `last_active` after every file write or command
2. **Rich checkpoints** — capture task, decisions, files, and open questions on demand
3. **One-keystroke restore** — recover full context in a new session in seconds
4. **Multi-project dashboard** — see all active sessions across directories
5. **Checkpoint diff** — compare what changed between saves

## Installation

### Quick Install

In Claude Code, say:

> "Help me install fireworks-sessions-saver from https://github.com/yizhiyanhua-ai/fireworks-sessions-saver"

Or run:

```bash
curl -fsSL https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/install.sh | bash
```

### npx skills Install

```bash
npx skills add yizhiyanhua-ai/fireworks-sessions-saver -g
```

## How It Works

A single `PostToolUse` hook fires `heartbeat.py` asynchronously after every `Write`, `Edit`, or `Bash` call — updating `last_active` and tracking modified files.

| Component | Purpose |
|-----------|---------|
| `heartbeat.py` | Lightweight async hook — tracks activity after tool calls |
| `save_session.py` | Create rich checkpoints (init / checkpoint / cleanup) |
| `list_sessions.py` | Scan for recoverable sessions in current directory |
| `restore_session.py` | Print structured context summary from archive |
| `dashboard.py` | View all active sessions across directories |
| `diff_session.py` | Compare changes between checkpoints |

### Storage

```
~/.claude/sessions/
  active_{workdir_hash}.json          ← current session (rolling 10 checkpoints)
  archive_{workdir_hash}_{ts}.json    ← archived (restored or expired after 7 days)
```

Only file **paths** are stored — never file contents.

## Requirements

- Python 3.9+
- Claude Code CLI
- macOS / Linux

## More Information

- [Full Documentation](README.md)
- [中文文档](README.zh-CN.md)
- [Report Bug](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues)
