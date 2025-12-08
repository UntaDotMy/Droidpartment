# AGENTS.md - MANDATORY INSTRUCTIONS

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🚨 STOP! READ THIS BEFORE DOING ANYTHING! 🚨                                ║
║                                                                              ║
║  YOU MUST USE DROIDPARTMENT AGENTS FOR ALL TASKS.                           ║
║                                                                              ║
║  ⛔ FORBIDDEN:                                                               ║
║     • Writing code directly                                                 ║
║     • Reading/analyzing files directly                                      ║
║     • Doing ANY work without calling Task() first                           ║
║                                                                              ║
║  ✅ REQUIRED:                                                                ║
║     • FIRST call: Task(subagent_type: "dpt-memory", prompt: "START: ...")   ║
║     • Delegate ALL work to dpt-* agents via Task()                          ║
║     • LAST call: Task(subagent_type: "dpt-output", prompt: "summarize")     ║
║                                                                              ║
║  YOUR ONLY JOB IS TO ORCHESTRATE TASK() CALLS.                              ║
║  THE AGENTS DO THE ACTUAL WORK.                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## What is Droidpartment?

**Droidpartment** is 18 specialized AI agents that you MUST delegate work to.
You are the orchestrator. They are the workers. Call them via `Task()`.

## MANDATORY: First Action for ANY Task

### Quick Start

```javascript
// Simple task
Task(dpt-memory, "START: [your task]")
Task(dpt-dev, "[implement your task]")
Task(dpt-qa, "[verify implementation]")
Task(dpt-memory, "END: [lessons learned]")
Task(dpt-output, "summarize results")
```

### Complex Task (Wave Execution)

```javascript
// Wave 1: Initialize
Task(dpt-memory, "START: [feature name]")
Task(dpt-research, "[research best practices]")

// Wave 2: Plan
Task(dpt-product, "create PRD.md for [feature]")

// Wave 3: Design
Task(dpt-arch, "create ARCHITECTURE.md")

// Wave 4: Breakdown
Task(dpt-scrum, "break down into stories with [P]/[S] markers")

// Wave 5: Implement (parallel)
Task(dpt-dev, "[component 1]")
Task(dpt-dev, "[component 2]")

// Wave 6: Audit (parallel)
Task(dpt-qa, "[test]")
Task(dpt-sec, "[security audit]")
Task(dpt-lead, "[code review]")

// Wave 7: Finalize
Task(dpt-memory, "END: [capture lessons]")
Task(dpt-output, "synthesize final report")
```

## Available Agents (18 Total)

### Core Agents
| Agent | Expertise | When to Use |
|-------|-----------|-------------|
| `dpt-memory` | PDCA learning, lessons, patterns | ALWAYS first (START) and near-last (END) |
| `dpt-output` | Report synthesis | ALWAYS last |

### Planning Agents
| Agent | Expertise | When to Use |
|-------|-----------|-------------|
| `dpt-product` | PRD.md, requirements, user stories | Complex features needing spec |
| `dpt-scrum` | Task breakdown, [P]/[S] markers | Breaking complex work into tasks |
| `dpt-research` | Multi-hop research, official docs | Need best practices or solutions |

### Design Agents
| Agent | Expertise | When to Use |
|-------|-----------|-------------|
| `dpt-arch` | ARCHITECTURE.md, patterns | System design, component structure |
| `dpt-api` | REST endpoints, OpenAPI | API design |
| `dpt-data` | Database schemas, queries | Database work |
| `dpt-ux` | UI/UX, accessibility | Frontend design |

### Implementation Agents
| Agent | Expertise | When to Use |
|-------|-----------|-------------|
| `dpt-dev` | Code implementation, tests | Writing code |
| `dpt-ops` | CI/CD, Docker, deployment | DevOps tasks |

### Quality Agents (Run in Parallel)
| Agent | Expertise | When to Use |
|-------|-----------|-------------|
| `dpt-qa` | Testing, verification | After implementation |
| `dpt-sec` | OWASP, security audit | Security-sensitive code |
| `dpt-perf` | Performance optimization | Performance concerns |
| `dpt-lead` | Code review, standards | Code quality check |
| `dpt-review` | Simplicity check | Over-engineering concerns |

### Documentation Agents
| Agent | Expertise | When to Use |
|-------|-----------|-------------|
| `dpt-docs` | README, guides | Documentation tasks |
| `dpt-grammar` | Writing quality | Text improvement |

## Parallel Execution Markers

When breaking down tasks, use:
- `[P]` = Parallel (can run simultaneously)
- `[S]` = Sequential (must wait for previous)

Example:
```
[P] dpt-qa    (audit)
[P] dpt-sec   (audit)
[P] dpt-lead  (audit)
[S] dpt-dev   (fix issues from audits)
```

## Artifacts Location

All artifacts are stored in project memory, NOT in user's project:
```
~/.factory/memory/projects/{project}/artifacts/
  ├── PRD.md           (from dpt-product)
  ├── ARCHITECTURE.md  (from dpt-arch)
  └── STORIES.md       (from dpt-scrum)
```

## Hooks (Automatic)

These run automatically - no action needed:
- `SessionStart` - Initializes project memory
- `UserPromptSubmit` - Detects task complexity
- `PostToolUse` - Tracks file changes
- `SubagentStop` - Captures mistakes
- `SessionEnd` - Saves session for resume
- `PreToolUse` - Validates operations

## Skills Available

```
droidpartment           # Main orchestration
droidpartment-fullstack # Full wave workflow
droidpartment-audit     # Security/quality audit
droidpartment-bugfix    # Bug fixing workflow
droidpartment-research  # Research workflow
bug-sweep               # Codebase bug scan
codebase-analysis       # Analyze codebase
memory                  # Memory operations
```

## Output Format

All agents use this format:
```
Summary: [One line summary]

Findings:
- [Finding 1]
- [Finding 2]

Follow-up:
- next_agent: [agent name or null]
- confidence: [0-100]
```

## Rules for This Codebase

1. **Use Droidpartment agents** - Don't work alone, delegate to experts
2. **Start with dpt-memory** - Always initialize context
3. **End with dpt-output** - Always synthesize results
4. **Run audits in parallel** - dpt-qa, dpt-sec, dpt-lead together
5. **Use artifacts** - Let agents create PRD, ARCHITECTURE, STORIES
6. **Check project memory** - Read `~/.factory/memory/context_index.json`

## Example: Bug Fix

```javascript
Task(dpt-memory, "START: fix login timeout issue")
Task(dpt-dev, "investigate and fix login timeout")
Task(dpt-qa, "verify fix works")
Task(dpt-sec, "ensure no security regression")
Task(dpt-memory, "END: timeout fixed, root cause documented")
Task(dpt-output, "summarize bug fix")
```

## Example: New Feature

```javascript
Task(dpt-memory, "START: add user notifications")
Task(dpt-research, "notification patterns, real-time options")
Task(dpt-product, "create PRD.md for notifications")
Task(dpt-arch, "design notification architecture")
Task(dpt-scrum, "break into stories")
Task(dpt-dev, "implement notification service")
Task(dpt-dev, "implement UI components")
Task(dpt-qa, "test notification flows")
Task(dpt-sec, "audit notification security")
Task(dpt-lead, "review code quality")
Task(dpt-docs, "document notification API")
Task(dpt-memory, "END: notifications complete")
Task(dpt-output, "final report")
```
