# Droidpartment

**19 AI Agents for Factory AI** - Autonomous software development team with memory system.

## Quick Start

```bash
npx droidpartment
```

Then enable in Factory: `/settings` → Experimental → Custom Droids → Restart CLI

## How Droids Get Triggered

Custom droids are invoked via the **Task tool** in two ways:

1. **Automatic** - Main droid reads the `description` and decides to use the right agent
2. **Manual** - You ask: "Use subagent `DPT_CHIEF` to build this feature"

**What gets installed:**

| Item | Location | Purpose |
| :--- | :--- | :--- |
| 19 Droids | `~/.factory/droids/` | Specialized agents |
| AGENTS.md | `~/.factory/AGENTS.md` | Guides main droid to use DPT_CHIEF |
| Memory | `~/.factory/memory/` | Learning system |

**With AGENTS.md:** Main droid is instructed to delegate to DPT_CHIEF for all tasks.

**Without AGENTS.md:** Main droid can still use droids based on their descriptions, or you ask manually.

## Agents

| Type | Agents |
| :--- | :--- |
| **Leader** | DPT_CHIEF (orchestrates everything) |
| **Core** | MEMORY, RESEARCH, SCRUM, PRODUCT, ARCH, DEV, LEAD, QA, SEC, OPS |
| **Specialists** | DOCS, DATA, PERF, UX, API, GRAMMAR, REVIEW, OUTPUT |

## How It Works

```
You: "Add login feature"
         ↓
Main Droid → calls DPT_CHIEF via Task tool
         ↓
DPT_CHIEF delegates to team → validates → delivers
         ↓
Production-ready code
```

## Memory System

- **Global lessons** - Shared across all projects
- **Per-project memory** - Never mixed between projects
- **Grows smarter** - More sessions = less mistakes

## Commands

| Command | Description |
| :--- | :--- |
| `npx droidpartment` | Install or update |
| `npx droidpartment --memory` | View and clean memory |
| `npx droidpartment --uninstall` | Remove everything |

## Philosophy

```
SIMPLE > COMPLEX
READABLE > CLEVER
DO WHAT'S REQUESTED > SURPRISE USER
```

## Requirements

- Node.js >= 16
- Factory AI Droid CLI
- Custom Droids enabled

## Changelog

### v1.0.4
- **CRITICAL FIX:** Filenames now match name field (Factory requirement)
- Fixed: `chief.md` → `dpt-chief.md`, `developer.md` → `dpt-dev.md`, etc.
- Droids now properly discovered by Factory AI

### v1.0.3
- Added auto-trigger skill for automatic delegation
- Simplified AGENTS.md (shorter, clearer instructions)
- Skills are auto-invoked by Factory AI based on task

### v1.0.2
- **CRITICAL FIX:** Changed all agent names to lowercase (Factory AI requires lowercase)
- Fixed: `DPT_CHIEF` → `dpt-chief`, `DPT_DEV` → `dpt-dev`, etc.
- Droids now properly recognized by Factory AI

### v1.0.1
- Improved dpt-chief description for better automatic triggering
- Fixed uninstall to completely remove memory folder
- Added edge case handling
- Updated documentation

### v1.0.0
- Initial release
- 19 specialized AI agents
- Memory system (global lessons + per-project)
- AGENTS.md for automatic delegation
- Install/update/uninstall commands

## License

MIT
