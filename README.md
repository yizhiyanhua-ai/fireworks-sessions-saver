<div align="center">

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/logo.svg" alt="fireworks-sessions-saver" width="80" />

# fireworks-sessions-saver

**Never lose your coding session context again.**

Automatically persists and restores session state for Claude Code. Codex support coming soon.

[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-supported-8A2BE2)](https://claude.ai/code)
[![Codex](https://img.shields.io/badge/Codex-planned-gray.svg)](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues)
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

In Claude Code or Codex, just say:

> *"Install fireworks-sessions-saver from https://github.com/yizhiyanhua-ai/fireworks-sessions-saver"*

---

## How It Works

### Architecture

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/architecture.svg" alt="Architecture" width="100%"/>

**Left — Tracking flow:** Every `Write`, `Edit`, or `Bash` call fires `heartbeat.py` asynchronously (&lt;5ms), updating `last_active` and merging git-modified file paths into the active session file. When you say "save session", a rich checkpoint is written — capturing the current task, key decisions, open questions, file references, git branch, and log paths. On the next session init, the active file is archived.

**Right — Recovery flow:** When a new session opens, `list_sessions.py` automatically scans for sessions in the same working directory active within the last 7 days. After you select one, `restore_session.py` prints a structured context summary. Once the first new checkpoint is saved, the archive file is deleted — no stale files accumulate.

### Components

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/components.svg" alt="Components" width="100%"/>

Four layers, top to bottom:

- **CLI Tools** — Claude Code and Codex are the primary supported tools; the architecture is open to any coding CLI.
- **Hook Layer** — A single `PostToolUse` hook in `settings.json` fires `heartbeat.py` asynchronously after every file write or shell command. Zero impact on your workflow.
- **Scripts** — Four focused Python scripts: `heartbeat.py` (auto, lightweight), `save_session.py` (init / checkpoint / cleanup), `list_sessions.py` (scan & rank), `restore_session.py` (format & print).
- **Storage** — Two JSON file types in `~/.claude/sessions/`: `active_{hash}.json` for the running session (rolling 10 checkpoints), and `archive_{hash}_{ts}.json` for sessions awaiting restore or expiry.

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

### View all sessions (dashboard)
Say any of:
- `dashboard` / `show all sessions` / `which projects are active`
- `查看所有 session` / `多项目看板`

Claude will run the dashboard and show all active sessions across every working directory.

```bash
# Manual CLI usage
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/dashboard.py
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/dashboard.py --all   # include expired
```

### Diff two checkpoints
Say any of:
- `diff checkpoint` / `what changed since last checkpoint`
- `对比进度` / `两次 checkpoint 有什么变化`

Claude will compare the last two checkpoints and show what changed in task, files, decisions, and open questions.

```bash
# Manual CLI usage
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/diff_session.py \
  --session-file ~/.claude/sessions/active_<hash>.json
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/diff_session.py \
  --session-file ~/.claude/sessions/active_<hash>.json --list   # list all checkpoints
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/diff_session.py \
  --session-file ~/.claude/sessions/active_<hash>.json --from 2 --to 4
```

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
- Claude Code CLI
- macOS / Linux

> **Codex CLI**: Hook-based auto-tracking is not yet supported (Codex does not have a hook system). Manual checkpoint and restore via the scripts still work. Full Codex support is on the roadmap.

---

## Roadmap

- [x] Claude Code — full auto-tracking via PostToolUse hook
- [ ] Codex CLI — auto-tracking support ([planned](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues))
- [x] Session diff view — show what changed between checkpoints
- [x] Multi-project dashboard — view all active sessions across directories

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
│       ├── heartbeat.py              ← lightweight async hook
│       ├── diff_session.py           ← diff two checkpoints
│       └── dashboard.py              ← multi-project session dashboard
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
