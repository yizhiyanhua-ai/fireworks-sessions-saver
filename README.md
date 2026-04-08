<div align="center">

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/logo.svg" alt="fireworks-sessions-saver" width="80" />

# fireworks-sessions-saver

**Never lose your coding session context again.**

Automatically persists and restores session state across Claude Code, Codex, and other coding CLI tools.

[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-8A2BE2)](https://claude.ai/code)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/pulls)

[中文文档](README.zh-CN.md) · [Report Bug](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues) · [Request Feature](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues)

</div>

---

## The Problem

Network timeouts, crashes, and accidental window closures kill your session context. Re-establishing it in a new window wastes time and tokens.

```
Session 1:  Deep in a complex refactor — network drops               ✗ context gone
New session: "What were we working on?" — 10 minutes re-explaining   ✗ expensive
```

## The Solution

`fireworks-sessions-saver` automatically tracks what you're working on and makes it instantly available when you reconnect — in any new Claude Code or Codex window.

```
Session 1:  Working on auth refactor → auto-tracked every tool call
            Network drops
New session: "Found 1 previous session — restore?" → one keystroke   ✓ back in 5 seconds
```

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/install.sh | bash
```

Then type `/hooks` in Claude Code to activate — that's it.

---

## How It Works

### Architecture

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/architecture.svg" alt="Architecture" width="100%"/>

### Components

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/components.svg" alt="Components" width="100%"/>

---

## Usage

### Automatic (via hook)
The heartbeat runs silently after every `Write`, `Edit`, or `Bash` call. No action needed.

### Save a rich checkpoint
Say any of:
- `save session` / `save progress`
- `保存进度` / `保存状态`

Claude will capture: current task, files in context, key decisions, open questions, recent commands, and log file paths.

### Restore a previous session
In a new window, Claude automatically checks for recoverable sessions on startup. Or say:
- `restore session` / `continue from last session`
- `恢复会话` / `继续之前的工作`

### Manual CLI usage
```bash
# List recoverable sessions for current directory
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/list_sessions.py

# Restore a specific session
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/restore_session.py \
  --session-file ~/.claude/sessions/archive_abc12345_20260408_143022.json
```

---

## Storage

```
~/.claude/sessions/
  active_{workdir_hash}.json          ← current active session
  archive_{workdir_hash}_{ts}.json    ← archived (awaiting restore or expiry)
```

- Sessions expire after **7 days** of inactivity
- Each file holds at most **10 checkpoints** (rolling window)
- Only file **paths** are stored — never file contents
- Archived files are deleted after successful transfer to a new session

---

## Requirements

- Python 3.9+
- Claude Code CLI (or Codex CLI)
- macOS / Linux

---

## Project Structure

```
fireworks-sessions-saver/
├── skill/
│   ├── SKILL.md                      ← Claude Code skill definition
│   ├── references/
│   │   ├── session-format.md         ← JSON schema docs
│   │   └── log-discovery.md          ← Claude Code / Codex log locations
│   └── scripts/
│       ├── save_session.py           ← init / checkpoint / cleanup
│       ├── list_sessions.py          ← find recoverable sessions
│       ├── restore_session.py        ← print structured context summary
│       └── heartbeat.py              ← lightweight async hook
├── install.sh
├── LICENSE
├── README.md
└── README.zh-CN.md
```

---

## Contributing

PRs welcome. Please open an issue first for significant changes.

## License

[MIT](LICENSE)
