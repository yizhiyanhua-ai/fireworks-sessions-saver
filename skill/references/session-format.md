# Session File JSON Schema

## File Naming

| Pattern | Purpose |
|---------|---------|
| `active_{workdir_hash}.json` | Currently active session for a working directory |
| `archive_{workdir_hash}_{timestamp}.json` | Archived session (from a previous run) |

`workdir_hash` = first 8 chars of `MD5(absolute_working_dir_path)`  
`timestamp` = `YYYYMMDD_HHMMSS` (UTC)

---

## Top-Level Fields

```json
{
  "session_id": "a1b2c3d4",
  "tool": "claude-code",
  "working_dir": "/absolute/path/to/project",
  "start_time": "2026-04-08T10:00:00",
  "last_active": "2026-04-08T11:30:00",
  "status": "active",
  "checkpoints": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | 8-char random hex ID |
| `tool` | string | `"claude-code"` or `"codex"` |
| `working_dir` | string | Absolute path to project directory |
| `start_time` | ISO8601 | When this session was created |
| `last_active` | ISO8601 | Last heartbeat or checkpoint time |
| `status` | string | `"active"`, `"transferred"` |
| `checkpoints` | array | Up to 10 checkpoint objects (rolling window) |

---

## Checkpoint Object

```json
{
  "timestamp": "2026-04-08T11:30:00",
  "summary": "Implementing JWT auth middleware",
  "current_task": "Fix token expiry logic in src/auth.ts",
  "git_branch": "feature/auth",
  "git_recent_commits": [
    "abc1234 Add JWT validation middleware",
    "def5678 Setup auth route handlers"
  ],
  "files": [
    {
      "path": "/abs/path/src/auth.ts",
      "last_modified": "2026-04-08T11:25:00",
      "role": "editing",
      "note": "Adding token refresh logic"
    },
    {
      "path": "/abs/path/tests/auth.test.ts",
      "last_modified": "2026-04-08T11:10:00",
      "role": "reference",
      "note": ""
    }
  ],
  "key_decisions": [
    "Using RS256 over HS256 for multi-service token verification"
  ],
  "open_questions": [
    "API response format for expired token — 401 or 403?"
  ],
  "recent_commands": [
    "git status",
    "npm test -- --grep auth"
  ],
  "log_refs": {
    "claude_code": "~/.claude/projects/abc12345/conversations/2026-04-08.jsonl",
    "codex": null
  }
}
```

### Checkpoint Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO8601 | When checkpoint was saved |
| `summary` | string | One-line description of current state |
| `current_task` | string | Specific task in progress |
| `git_branch` | string | Current git branch (null if not a git repo) |
| `git_recent_commits` | string[] | Last 3–5 `git log --oneline` entries |
| `files` | FileRef[] | Files in context (paths only, never content) |
| `key_decisions` | string[] | Important decisions made this session |
| `open_questions` | string[] | Unresolved questions or blockers |
| `recent_commands` | string[] | Shell commands recently run |
| `log_refs` | object | Paths to tool log files for deeper context |

### FileRef Fields

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Absolute file path |
| `last_modified` | ISO8601 | File mtime at checkpoint time |
| `role` | string | `"editing"`, `"reference"`, `"created"`, `"deleted"` |
| `note` | string | Brief note on what was being done with this file |

---

## Status Values

| Status | Meaning |
|--------|---------|
| `active` | Session is currently running or was recently active |
| `transferred` | Context was restored into a new session; safe to delete |
