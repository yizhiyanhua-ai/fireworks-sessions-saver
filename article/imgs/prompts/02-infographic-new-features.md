---
type: infographic
style: dark-tech
aspect: 16:9
filename: 02-infographic-new-features.png
---

# ZONES
TOP ZONE (15%): Title bar "fireworks-sessions-saver — New Features v1.1"
LEFT HALF (42%): Dashboard panel showing multi-project session list
RIGHT HALF (42%): Diff panel showing checkpoint comparison
CENTER DIVIDER (6%): Vertical separator with "+" icon

# LABELS
Left panel title: "📊 Multi-Project Dashboard"
Left panel content:
  "SESSION DASHBOARD — 3 active"
  "[1] /projects/auth-service  3 CPs"
  "    Task: JWT middleware refactor"
  "[2] /projects/frontend  1 CP"
  "    Task: Fix login page styles"
  "[3] /projects/api  2 CPs"
  "    Task: Rate limiting impl"
Left trigger: 'Say: "查看所有 session"'

Right panel title: "🔍 Checkpoint Diff"
Right panel content:
  "DIFF [2] → [3]"
  "── Task ──────────────"
  "  - Analyze auth arch"
  "  + Implement JWT refresh"
  "── Files ─────────────"
  "  + src/auth/refresh.ts"
  "  ~ middleware.ts → editing"
  "── Decisions ─────────"
  "  + httpOnly cookie storage"
Right trigger: 'Say: "对比进度"'

# COLORS
Background: #0f0f1a → #1a1a2e gradient
Left panel: #0a1a0f border #10b981 (green)
Right panel: #1a0a2e border #a855f7 (purple)
Title bar: #0f172a border #334155
Added lines (+): #10b981
Removed lines (-): #ef4444
Changed lines (~): #f97316
Text primary: #e2e8f0
Text secondary: #94a3b8
Trigger badges: #1e3a5f border #3b82f6

# STYLE
Dark terminal aesthetic, monospace font SF Mono / Fira Code, code-editor look, clean grid layout, subtle glow on panel borders, professional tech illustration
