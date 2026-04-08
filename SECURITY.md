# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✓         |

## Reporting a Vulnerability

Please do **not** open a public GitHub issue for security vulnerabilities.

Instead, report them via GitHub's private vulnerability reporting:
**Security → Report a vulnerability** on the repository page.

We aim to respond within 48 hours and will coordinate a fix and disclosure timeline with you.

## Scope

This project runs locally on your machine and stores session data in `~/.claude/sessions/`. It does not transmit any data externally. The main security considerations are:

- Session files may contain file paths and task summaries from your projects — treat `~/.claude/sessions/` as sensitive
- The heartbeat hook runs after every `Write`/`Edit`/`Bash` tool call — review the hook command in your `settings.json` if you have concerns
