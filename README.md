# Droidpartment

**Autonomous Software Development Department** - 18 specialized AI agents (DPT_*) with team leader, memory, and dynamic collaboration for Factory AI Droid CLI.

Simple. Maintainable. Led by DPT_CHIEF. Production ready.

## Installation

```bash
npx droidpartment
```

## Uninstall

```bash
npx droidpartment --uninstall
```

## What You Get

A complete autonomous software development team with 18 specialized agents:

### Leader
| Agent | Role |
|-------|------|
| **DPT_CHIEF** | **TEAM LEADER** - Entry point, delegates, validates, ensures production-ready |

### Core Team
| Agent | Role |
|-------|------|
| **DPT_MEMORY** | Human-like learning system |
| **DPT_RESEARCH** | Deep research, official sources first |
| **DPT_SCRUM** | Task decomposition, DAG |
| **DPT_PRODUCT** | Requirements, user stories |
| **DPT_ARCH** | System design, patterns |
| **DPT_DEV** | Implementation, coding |
| **DPT_LEAD** | Code review, SOLID |
| **DPT_QA** | Testing strategies |
| **DPT_SEC** | OWASP 2025, vulnerabilities |
| **DPT_OPS** | CI/CD, deployment |

### Specialists
| Agent | Role |
|-------|------|
| **DPT_DOCS** | Clear docs (when requested) |
| **DPT_DATA** | Schema, queries, data |
| **DPT_PERF** | Optimization (measure first) |
| **DPT_UX** | Simple, accessible interfaces |
| **DPT_API** | RESTful, consistent APIs |
| **DPT_GRAMMAR** | Grammar, clarity, readability |
| **DPT_REVIEW** | Anti-over-engineering guard |

## Memory System (Human-Like Learning)

The department learns like a human:

```
MISTAKE → FIX → USER CONFIRMS → CAPTURE LESSON
                                      │
                                      ▼
NEXT SIMILAR ISSUE → RETRIEVE LESSON → APPLY KNOWLEDGE
```

**Auto-Capture**: When you say "it works!" or "fixed!" the system:
1. Summarizes what was learned (1-3 sentences)
2. Tags for future retrieval
3. Stores in project-specific memory

**Auto-Retrieve**: Before any fix, the system:
1. Checks past lessons
2. Applies learned patterns
3. Avoids repeated mistakes

**Per-Project**: Each project has its own memory in `.factory/memory/`

## Philosophy

```
SIMPLE > COMPLEX
READABLE > CLEVER
LEARN FROM MISTAKES
```

## Features

- **Memory System**: Learns from mistakes, gets smarter over time
- **Fully Autonomous**: Just describe your task
- **Research-First**: Always uses current best practices
- **Anti-Over-Engineering**: Reviewer agent blocks complexity
- **Beginner-Friendly**: Code readable by all skill levels

## Installation Options

When you run `npx droidpartment`, you'll be asked:

1. **Personal** (default): `~/.factory/droids/`
   - Available in ALL projects automatically
   - No per-project setup needed

2. **Project**: `./.factory/droids/`
   - Only available in current project
   - Can be committed to version control

## Usage

After installation:

1. Enable Custom Droids in Factory: `/settings` → Experimental → Custom Droids
2. Restart your droid CLI
3. Just describe what you want!

### Examples

```
"Add a user authentication feature"
→ Activates: RESEARCH → SM → PO → ARCH → DEV → TL → QA → SEC

"Fix the login bug"
→ Activates: RESEARCH → SM → DEV → TL → QA

"Security audit the payment module"
→ Activates: RESEARCH → SEC → TL → DEV

"Research best practices for caching in Node.js"
→ Activates: RESEARCH (deep)
```

## How It Works

```
Your Request
     │
     ▼
┌─────────────────────────────────────┐
│  1. MEMORY: Check past lessons      │
│  2. AUTO-DETECT task type           │
│  3. RESEARCH current best practices │
│  4. EXECUTE with quality gates      │
│  5. DELIVER production-ready code   │
│  6. CAPTURE: Learn from success     │
└─────────────────────────────────────┘
```

## CLI Flags

```bash
npx droidpartment              # Interactive install
npx droidpartment --yes        # Auto-install to personal
npx droidpartment --project    # Install to current project
npx droidpartment --uninstall  # Remove all agents
npx droidpartment -u           # Same as --uninstall
```

## Requirements

- Node.js >= 16.0.0
- Factory AI Droid CLI installed
- Custom Droids enabled in Factory settings

## License

MIT
