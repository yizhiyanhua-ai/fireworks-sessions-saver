---
name: fireworks-sessions-saver
description: Session state persistence and recovery for coding CLI tools (Claude Code, Codex). ALWAYS use this skill when: (1) starting any new session — proactively check for recoverable previous sessions from the same working directory, (2) user says "save session", "checkpoint", "save progress", "记录进度", "保存状态", (3) user says "restore session", "context lost", "continue from", "reconnect", "恢复会话", "继续之前的工作", (4) after a crash or network timeout. Do not wait for the user to ask — check for stale sessions at every session start.
---

# fireworks-sessions-saver

Persists and restores coding session state across Claude Code, Codex, and other CLI tools. Prevents context loss from network timeouts, crashes, or accidental window closures.

## Storage Layout

```
~/.claude/sessions/
  active_{workdir_hash}.json          ← current active session for this working dir
  archive_{workdir_hash}_{ts}.json    ← archived sessions (from previous runs)
```

- `workdir_hash` = first 8 chars of MD5 of the absolute working directory path
- Sessions with `last_active` older than **7 days** are expired and skipped
- Each session file holds at most **10 checkpoints** (rolling window — oldest dropped)

---

## Workflow

### 1. Session Start — Check for Recoverable Sessions

Run:
```bash
python ~/.claude/skills/fireworks-sessions-saver/scripts/list_sessions.py "$(pwd)"
```

If recoverable sessions are found (last_active < 7 days), present them:
```
Found 1 previous session for this project:
  [2026-04-07 14:30, 1 day ago] claude-code
  Task: "Implementing JWT auth middleware"
  Files: src/auth.ts, tests/auth.test.ts
  Open questions: API response format TBD

Restore this session? (y/n)
```

If user says yes → run the restore workflow (section 3).

Then always create/reset the active session:
```bash
python ~/.claude/skills/fireworks-sessions-saver/scripts/save_session.py \
  --working-dir "$(pwd)" \
  --tool "claude-code" \
  --action init
```

### 2. Save a Checkpoint

Trigger: user asks to save, or at natural breakpoints (task complete, before risky ops, before ending session).

Gather from current context:
- What task is in progress right now
- Files recently created or edited (absolute paths)
- Key decisions made since last checkpoint
- Open questions or blockers
- Recent commands run

Then run:
```bash
python ~/.claude/skills/fireworks-sessions-saver/scripts/save_session.py \
  --working-dir "$(pwd)" \
  --tool "claude-code" \
  --action checkpoint \
  --summary "Brief description of current state" \
  --current-task "Specific task in progress" \
  --files "/abs/path/file1.ts:editing,/abs/path/file2.ts:reference" \
  --decisions "Decision 1; Decision 2" \
  --open-questions "Question 1; Question 2" \
  --commands "git status; npm test"
```

File roles: `editing`, `reference`, `created`, `deleted`

### 3. Restore a Session

```bash
python ~/.claude/skills/fireworks-sessions-saver/scripts/restore_session.py \
  --session-file ~/.claude/sessions/archive_{hash}_{ts}.json
```

The script outputs a structured context summary. Present it to the user and use it to re-establish context.

**Do NOT delete the archive file yet.** After the first checkpoint is saved in the new session, run:
```bash
python ~/.claude/skills/fireworks-sessions-saver/scripts/save_session.py \
  --working-dir "$(pwd)" \
  --action cleanup \
  --archive-file ~/.claude/sessions/archive_{hash}_{ts}.json
```

### 4. Log Discovery (Supplementary)

When restoring, enrich context by checking tool logs. See `references/log-discovery.md` for Claude Code and Codex log locations.

---

## Hook Setup

Add to `~/.claude/settings.json` to enable auto-heartbeat (updates `last_active` after tool use):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|Bash",
        "hooks": [{
          "type": "command",
          "command": "python ~/.claude/skills/fireworks-sessions-saver/scripts/heartbeat.py \"$PWD\""
        }]
      }
    ]
  }
}
```

The heartbeat is lightweight — it only updates `last_active` and records recently touched files. Rich checkpoints (with task summaries, decisions, etc.) are created by the AI.

---

## File Reference Format

Files are stored as paths + metadata, never content:
```json
{
  "path": "/absolute/path/to/file.ts",
  "last_modified": "2026-04-08T10:30:00",
  "role": "editing",
  "note": "Adding JWT validation logic"
}
```

See `references/session-format.md` for the full session JSON schema.
