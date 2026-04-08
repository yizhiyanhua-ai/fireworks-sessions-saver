#!/usr/bin/env bash
# fireworks-sessions-saver — one-command installer
# Usage: curl -fsSL https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/install.sh | bash

set -euo pipefail

REPO="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main"
SKILL_DIR="$HOME/.claude/skills/fireworks-sessions-saver"
SETTINGS="$HOME/.claude/settings.json"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC}  $*"; }
error() { echo -e "${RED}✗${NC} $*"; exit 1; }

echo ""
echo "🔥 fireworks-sessions-saver installer"
echo "──────────────────────────────────────"
echo ""

# ── 1. Preflight ───────────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || error "Python 3 is required but not found."
command -v claude  >/dev/null 2>&1 || error "Claude Code CLI not found. Install from https://claude.ai/code"

PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
[[ "$PY_MINOR" -lt 9 ]] && error "Python 3.9+ required (found 3.$PY_MINOR)"

info "Python $(python3 --version) found"
info "Claude Code found at $(command -v claude)"

# ── 2. Create directories ──────────────────────────────────────────────────────
mkdir -p "$SKILL_DIR/scripts"
mkdir -p "$SKILL_DIR/references"
mkdir -p "$HOME/.claude/sessions"
info "Directories ready"

# ── 3. Download skill files ────────────────────────────────────────────────────
echo ""
echo "📥 Downloading skill files..."

for f in SKILL.md; do
  curl -fsSL "$REPO/skill/$f" -o "$SKILL_DIR/$f"
  info "$f"
done

for f in session-format.md log-discovery.md; do
  curl -fsSL "$REPO/skill/references/$f" -o "$SKILL_DIR/references/$f"
  info "references/$f"
done

for f in save_session.py list_sessions.py restore_session.py heartbeat.py diff_session.py dashboard.py; do
  curl -fsSL "$REPO/skill/scripts/$f" -o "$SKILL_DIR/scripts/$f"
  info "scripts/$f"
done

# ── 4. Syntax check ────────────────────────────────────────────────────────────
for f in save_session.py list_sessions.py restore_session.py heartbeat.py diff_session.py dashboard.py; do
  python3 -m py_compile "$SKILL_DIR/scripts/$f" || error "Syntax error in $f"
done
info "All scripts verified (syntax OK)"

# ── 5. Patch settings.json ─────────────────────────────────────────────────────
echo ""
echo "⚙️  Configuring heartbeat hook in $SETTINGS ..."

[[ ! -f "$SETTINGS" ]] && echo '{}' > "$SETTINGS" && warn "Created new $SETTINGS"

python3 - "$SETTINGS" "$SKILL_DIR" <<'PYEOF'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
skill_dir     = sys.argv[2]

settings = json.loads(settings_path.read_text())
hooks = settings.setdefault("hooks", {})

new_hook = {
    "type": "command",
    "command": f"python3 {skill_dir}/scripts/heartbeat.py \"$PWD\"",
    "async": True,
}
post_entries = hooks.setdefault("PostToolUse", [])
already = any(
    e.get("matcher") == "Write|Edit|Bash" and any(
        h.get("command", "") == new_hook["command"]
        for h in e.get("hooks", [])
    )
    for e in post_entries
)
if not already:
    post_entries.append({"matcher": "Write|Edit|Bash", "hooks": [new_hook]})

# SessionStart hook — auto-init session on every new window
init_hook = {
    "type": "command",
    "command": f"python3 {skill_dir}/scripts/save_session.py --working-dir \"$PWD\" --tool claude-code --action init",
    "async": True,
}
start_entries = hooks.setdefault("SessionStart", [])
already_start = any(
    any(h.get("command", "") == init_hook["command"] for h in e.get("hooks", []))
    for e in start_entries
)
if not already_start:
    start_entries.append({"hooks": [init_hook]})

settings_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
print("OK")
PYEOF

info "Heartbeat hook registered"
info "SessionStart auto-init hook registered"

# ── 6. Done ────────────────────────────────────────────────────────────────────
echo ""
echo "──────────────────────────────────────"
echo -e "  ${GREEN}Installation complete!${NC}"
echo "──────────────────────────────────────"
echo ""
echo "  Next step → type  /hooks  in Claude Code to reload config."
echo ""
echo "  How it works:"
echo "  • Sessions are auto-tracked after every file write or bash command."
echo "  • On new session start, Claude checks for recoverable previous sessions."
echo "  • Say '保存进度' or 'save session' to create a rich checkpoint."
echo ""
echo "  Repo: https://github.com/yizhiyanhua-ai/fireworks-sessions-saver"
echo ""
