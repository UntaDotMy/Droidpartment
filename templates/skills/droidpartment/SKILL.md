---
name: droidpartment
description: 18 expert agents with PDCA learning system. Grows smarter every task.
---

# Droidpartment - 18 Experts + Memory

## HOW TO CALL AGENTS

**USE TASK TOOL, NOT SKILL TOOL!**

```javascript
Task(subagent_type: "dpt-memory", prompt: "START - [task type] for [project]")
```

## PDCA Learning Cycle

Every task follows Plan-Do-Check-Act:

```
PLAN  → memory(START), retrieve lessons, define scope
DO    → Execute with relevant experts
CHECK → Verify quality (parallel audits OK)
ACT   → memory(END), capture lessons, output
```

## Task Flows

### Feature Development
```
memory(START) → product → research → arch → scrum
     → dev → data/api/ux
     → qa + lead + sec + review (PARALLEL)
     → docs → memory(END) → output
```

### Bug Fix
```
memory(START) → research (reproduce)
     → 5 Whys (root cause) → dev → qa (regression test)
     → qa + lead + sec (PARALLEL)
     → memory(END) → output
```

### Audit
```
memory(START)
     → sec + lead + qa + review + perf (ALL PARALLEL)
     → memory(END) → output
```

### Research
```
memory(START) → research → arch (analyze)
     → review (simplest?)
     → memory(END) → output
```

### Improvement
```
memory(START) → perf (BASELINE)
     → dev (change) → perf (MEASURE)
     → qa + lead + sec (PARALLEL)
     → memory(END) → output
```

## The 18 Experts

| subagent_type | Role |
|---------------|------|
| dpt-memory | Learning system (START/END) |
| dpt-output | Format + stats (LAST) |
| dpt-product | Requirements |
| dpt-research | Best practices |
| dpt-arch | Architecture, ADRs |
| dpt-scrum | Task breakdown |
| dpt-dev | Implementation |
| dpt-data | Database |
| dpt-api | API design |
| dpt-ux | UI/UX |
| dpt-sec | Security (OWASP, CWE) |
| dpt-lead | Code review (SOLID) |
| dpt-qa | Testing (pyramid) |
| dpt-review | Simplicity (YAGNI) |
| dpt-perf | Performance |
| dpt-ops | DevOps |
| dpt-docs | Documentation |
| dpt-grammar | Grammar |

## Parallel vs Sequential

**PARALLEL OK:**
- sec + lead + qa + review + perf

**MUST BE SEQUENTIAL:**
- memory(START) → work → memory(END) → output
- perf(baseline) → change → perf(measure)

## Memory System

```
~/.factory/memory/
├── lessons.yaml     ← What worked
├── mistakes.yaml    ← What to avoid (+prevention)
├── patterns.yaml    ← Reusable solutions
└── projects/        ← Per-project knowledge
```

## Learning Metrics

```
IMPROVING:       prevented > new_mistakes
STABLE:          prevented = new_mistakes
NEEDS_ATTENTION: prevented < new_mistakes
```

## Output Format

```
MEMORY STATUS:
Project: <name>
Lessons: <n> (+<new>)
Mistakes: <n> (+<new>)
Prevented: <n>
Learning: Improving/Stable/Needs Attention
```

## Example: Audit

```javascript
// 1. Memory START - WAIT
Task(subagent_type: "dpt-memory", 
     prompt: "START - audit for MyProject")

// 2. Parallel experts
Task(subagent_type: "dpt-sec", prompt: "Security audit")
Task(subagent_type: "dpt-lead", prompt: "Code review")
Task(subagent_type: "dpt-qa", prompt: "Test coverage")

// 3. Memory END - WAIT (after experts)
Task(subagent_type: "dpt-memory",
     prompt: "END - findings: [results]")

// 4. Output - WAIT (after memory)
Task(subagent_type: "dpt-output",
     prompt: "Format with memory stats")
```
