# Droidpartment

**19 AI Agents for Factory AI** - Autonomous software development team with memory system.

## Quick Start

```bash
npx droidpartment
```

Then enable in Factory: `/settings` → Experimental → Custom Droids → Restart CLI

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
DPT_CHIEF receives → delegates to team → validates → delivers
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
| `npx droidpartment --uninstall` | Remove agents |

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

## License

MIT
