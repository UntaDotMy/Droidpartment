# Droidpartment v2.0

**19 AI Agents for Factory AI** - Autonomous software development department with PDCA cycle, real team collaboration, and memory that grows smarter over time.

## Installation

### Global Install (Recommended)

```bash
npm install -g droidpartment
```

Then run:
```bash
droidpartment
```

### One-time Use (npx)

```bash
npx droidpartment
```

### After Installation

Enable Custom Droids in Factory CLI:
1. Run `/settings`
2. Go to Experimental section
3. Enable Custom Droids
4. Restart CLI

## What's New in v2.0

### Department Workflow (Real Team Collaboration)
```
USER REQUEST
     │
     ▼
  MEMORY → RESEARCH → ARCH (Plan)
     │
     ▼
  ┌────────────────────────┐
  │   DEVELOPMENT LOOP     │
  │  DEV → LEAD → QA       │
  │   ↑      │      │      │
  │   └──────┴──────┘      │
  │   (back if issues)     │
  └────────────────────────┘
     │
     ▼
  SEC → REVIEW → MEMORY (Learn)
     │
     ▼
  DELIVER
```

### PDCA Cycle (Continuous Improvement)
- **PLAN**: Memory + Research + Architecture
- **DO**: Dev → Lead → QA (with back-and-forth loop)
- **CHECK**: Security + Review validation
- **ACT**: Capture lessons to memory (ALWAYS)

### Memory That Learns From Mistakes
```
~/.factory/memory/
├── lessons.yaml    ← Universal lessons
├── patterns.yaml   ← Successful patterns
├── mistakes.yaml   ← Mistakes to prevent (NEW)
└── projects/       ← Per-project knowledge
```

Over time: **Fewer mistakes, faster solutions, smarter predictions.**

## How It Works

```
You: "Add login feature"
         │
         ▼
    Main Droid → calls dpt-chief
         │
         ▼
    dpt-chief orchestrates:
    1. dpt-memory  → Check past lessons
    2. dpt-research → Find best practices
    3. dpt-arch    → Design solution
    4. dpt-dev     → Implement
         │
         ▼
    Development Loop (back-and-forth):
    dpt-dev → dpt-lead → dpt-qa
         │         │        │
         └─────────┴────────┘
              (until all pass)
         │
         ▼
    5. dpt-sec    → Security audit
    6. dpt-review → Simplicity check
    7. dpt-memory → Capture learnings
         │
         ▼
    Production-ready code + Smarter memory
```

## Agents (19 Total)

| Type | Agents |
| :--- | :--- |
| **Leader** | dpt-chief (orchestrates everything) |
| **Plan** | dpt-memory, dpt-research, dpt-scrum, dpt-product, dpt-arch |
| **Do** | dpt-dev, dpt-lead, dpt-qa |
| **Check** | dpt-sec, dpt-review |
| **Specialists** | dpt-docs, dpt-data, dpt-perf, dpt-ux, dpt-api, dpt-grammar, dpt-ops, dpt-output |

## Commands

After global install (`npm install -g droidpartment`):

| Command | Description |
| :--- | :--- |
| `droidpartment` | Install or update agents |
| `droidpartment --memory` | View and clean memory |
| `droidpartment --uninstall` | Remove everything |

Or use with npx:

| Command | Description |
| :--- | :--- |
| `npx droidpartment` | Install or update agents |
| `npx droidpartment --memory` | View and clean memory |
| `npx droidpartment --uninstall` | Remove everything |

## Memory Growth Model

```
Session 1:   Empty (like a newborn)
Session 5:   5 lessons, 2 patterns, 3 mistakes
Session 20:  25 lessons, 10 patterns, 8 mistakes
Session 100: 150+ lessons, rarely makes same mistake twice
```

## Philosophy

```
SIMPLE > COMPLEX
READABLE > CLEVER
DO WHAT'S REQUESTED > SURPRISE USER
LEARN FROM MISTAKES > REPEAT THEM
```

## Requirements

- Node.js >= 16
- Factory AI Droid CLI
- Custom Droids enabled (`/settings` → Experimental)

## Verified Compatible

Droidpartment follows [Factory's official Custom Droids specification](https://docs.factory.ai/cli/configuration/custom-droids):
- Valid YAML frontmatter with lowercase names
- Correct tool IDs (case-sensitive): `Read`, `Grep`, `Glob`, `LS`, `Create`, `Edit`, `Execute`, `WebSearch`, `FetchUrl`, `Task`
- Agents call each other via `Task` tool with `subagent_type` parameter
- Each agent has isolated context window

## Changelog

### v2.0.0
- **NEW: Department Workflow** - Real back-and-forth between agents (Dev → Lead → QA)
- **NEW: PDCA Cycle** - Plan-Do-Check-Act for continuous improvement
- **NEW: mistakes.yaml** - Captures mistakes with prevention steps
- **NEW: Knowledge Passing** - Agents pass structured knowledge to each other
- **ENHANCED: All 19 agents** with workflow sections and output formats
- **ENHANCED: dpt-memory** with auto-capture at start and end of every task
- Memory grows smarter over time (fewer repeated mistakes)

### v1.0.6
- Full audit: All 19 agent files updated with lowercase references
- Fixed ALL uppercase DPT_X references to lowercase dpt-x

### v1.0.5
- dpt-chief now correctly delegates using lowercase agent names

### v1.0.4
- Critical fix: Filenames now match name field (Factory requirement)

### v1.0.3
- Added auto-trigger skill for automatic delegation

### v1.0.2
- Critical fix: Changed all agent names to lowercase

### v1.0.0
- Initial release with 19 specialized AI agents

## License

MIT
