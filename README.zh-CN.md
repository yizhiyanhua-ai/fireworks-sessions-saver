<div align="center">

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/logo.svg" alt="fireworks-sessions-saver" width="80" />

# fireworks-sessions-saver

**再也不会丢失编程会话上下文。**

自动持久化并恢复 Claude Code 的会话状态。Codex 支持即将推出。

[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-supported-8A2BE2)](https://claude.ai/code)
[![Codex](https://img.shields.io/badge/Codex-planned-gray.svg)](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/pulls)

[English](README.md) · [提交 Bug](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues) · [功能建议](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues)

</div>

---

## 问题

网络超时、程序崩溃、不小心关掉窗口——会话上下文瞬间消失。在新窗口里重新建立上下文既浪费时间又浪费 token。

```
第 1 次：  正在做复杂的重构——网络断了                    ✗ 上下文全没了
新 session：「我们刚才在做什么？」——花 10 分钟重新解释    ✗ 代价高昂
```

## 解决方案

`fireworks-sessions-saver` 自动追踪你正在做的事，当你重新连接时——无论是哪个新窗口——立刻恢复现场。

```
第 1 次：  正在做 auth 重构 → 每次工具调用自动追踪
           网络断了
新 session：「发现 1 个历史 session——是否恢复？」→ 一键确认  ✓ 5 秒回到现场
```

---

## 安装

在 Claude Code 或 Codex 对话框里直接说：

> *"从 https://github.com/yizhiyanhua-ai/fireworks-sessions-saver 安装 fireworks-sessions-saver"*

---

## 工作原理

### 架构图

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/architecture.svg" alt="架构图" width="100%"/>

**左侧——追踪链路：** 每次 `Write`、`Edit`、`Bash` 调用都会异步触发 `heartbeat.py`（&lt;5ms），更新 `last_active` 并将 git 修改的文件路径合并进 session 文件。说"保存进度"时，写入完整 checkpoint——记录当前任务、关键决策、未解决问题、文件引用、git 分支和日志路径。下次 session 初始化时，当前文件自动归档。

**右侧——恢复链路：** 新 session 启动时，`list_sessions.py` 自动扫描同一工作目录下 7 天内有活动的历史 session。用户选择后，`restore_session.py` 输出结构化上下文摘要。新 session 保存第一个 checkpoint 后，归档文件自动删除，不会积累冗余文件。

### 组件图

<img src="https://raw.githubusercontent.com/yizhiyanhua-ai/fireworks-sessions-saver/main/docs/components.svg" alt="组件图" width="100%"/>

从上到下四层：

- **CLI 工具层** — 主要支持 Claude Code 和 Codex，架构对其他 coding CLI 工具开放扩展。
- **Hook 层** — `settings.json` 中一条 `PostToolUse` hook，在每次文件写入或命令执行后异步触发 `heartbeat.py`，对使用流程零影响。
- **脚本层** — 四个职责单一的 Python 脚本：`heartbeat.py`（自动、轻量）、`save_session.py`（初始化 / checkpoint / 清理）、`list_sessions.py`（扫描 & 排序）、`restore_session.py`（格式化 & 输出）。
- **存储层** — `~/.claude/sessions/` 下两类 JSON 文件：`active_{hash}.json` 存储当前 session（滚动 10 条 checkpoint），`archive_{hash}_{ts}.json` 存储等待恢复或过期的历史 session。

---

## 使用方式

### 自动（通过 hook）
心跳在每次 `Write`、`Edit`、`Bash` 调用后静默运行，无需任何操作。

### 保存完整 checkpoint
说任意一种：
- `保存进度` / `保存状态` / `save session`

Claude 会记录：当前任务、上下文文件、关键决策、未解决问题、最近命令、日志文件路径。

### 恢复历史 session
新窗口启动时 Claude 会自动检查可恢复的 session。也可以主动说：
- `恢复会话` / `继续之前的工作` / `restore session`

### 命令行手动使用
```bash
# 列出当前目录的可恢复 session
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/list_sessions.py

# 恢复指定 session
python3 ~/.claude/skills/fireworks-sessions-saver/scripts/restore_session.py \
  --session-file ~/.claude/sessions/archive_abc12345_20260408_143022.json
```

---

## 存储说明

```
~/.claude/sessions/
  active_{workdir_hash}.json          ← 当前活跃 session
  archive_{workdir_hash}_{ts}.json    ← 已归档（等待恢复或过期）
```

- session **7 天**无活动自动过期
- 每个文件最多保留 **10 条** checkpoint（滚动窗口）
- 只存储文件**路径**，从不存储文件内容
- 成功转移到新 session 后，归档文件自动删除

---

## 环境要求

- Python 3.9+
- Claude Code CLI
- macOS / Linux

> **Codex CLI**：基于 hook 的自动追踪暂不支持（Codex 没有 hook 系统）。手动 checkpoint 和恢复脚本仍可正常使用。完整 Codex 支持已列入计划。

---

## 路线图

- [x] Claude Code — 通过 PostToolUse hook 全自动追踪
- [ ] Codex CLI — 自动追踪支持（[计划中](https://github.com/yizhiyanhua-ai/fireworks-sessions-saver/issues)）
- [ ] Session diff 视图 — 展示两次 checkpoint 之间的变化
- [ ] 多项目看板 — 跨目录查看所有活跃 session

- Python 3.9+
- Claude Code CLI（或 Codex CLI）
- macOS / Linux

---

## 项目结构

```
fireworks-sessions-saver/
├── skill/
│   ├── SKILL.md                      ← Claude Code skill 定义
│   ├── references/
│   │   ├── session-format.md         ← JSON schema 文档
│   │   └── log-discovery.md          ← Claude Code / Codex 日志路径说明
│   └── scripts/
│       ├── save_session.py           ← 初始化 / checkpoint / 清理
│       ├── list_sessions.py          ← 查找可恢复 session
│       ├── restore_session.py        ← 输出结构化恢复摘要
│       └── heartbeat.py              ← 轻量级异步 hook
├── install.sh
├── LICENSE
├── README.md
└── README.zh-CN.md
```

---

## 贡献

欢迎 PR。重大改动请先开 issue 讨论。

## 许可证

[MIT](LICENSE)
