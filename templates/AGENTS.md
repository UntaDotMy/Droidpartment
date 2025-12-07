<coding_guidelines>
# Droidpartment - 18 Expert Agents

## HOW TO CALL AGENTS

**USE TASK TOOL, NOT SKILL TOOL!**

```javascript
Task(
  subagent_type: "dpt-memory",
  description: "Retrieve lessons",
  prompt: "START - [task type] for [project]"
)
```

## PDCA Learning Cycle (Every Task)

```
PLAN  → dpt-memory START, define scope, retrieve lessons
DO    → Execute with expert agents
CHECK → Verify quality, run audits (parallel OK)
ACT   → dpt-memory END, capture lessons, dpt-output
```

## Task Flows (Choose Based on Task Type)

### Feature Development
```
PLAN:  memory(START) → product → research → arch → scrum
DO:    dev → data/api/ux (as needed)
CHECK: qa + lead + sec + review + perf (PARALLEL)
ACT:   docs → memory(END) → output
```

### Bug Fix
```
PLAN:  memory(START) → research (reproduce)
DO:    5 Whys → dev (fix root cause) → qa (regression test)
CHECK: qa + lead + sec (PARALLEL)
ACT:   memory(END) → output (include prevention)
```

### Research / Understanding
```
PLAN:  memory(START) → define questions
DO:    research → arch (analyze)
CHECK: review (simplest approach?)
ACT:   memory(END) → output (with sources)
```

### Audit / Review
```
PLAN:  memory(START)
DO:    sec + lead + qa + review + perf (ALL PARALLEL)
CHECK: consolidate + prioritize
ACT:   memory(END) → output (action items)
```

### Improvement / Refactoring
```
PLAN:  memory(START) → perf (MEASURE BASELINE)
DO:    dev (small changes) → perf (MEASURE AFTER)
CHECK: qa + lead + sec + review (PARALLEL)
ACT:   memory(END) → output (before/after metrics)
```

## The 18 Experts

| Agent | Role | When to Use |
|-------|------|-------------|
| dpt-memory | Learning system | ALWAYS first and last |
| dpt-output | Format + stats | ALWAYS last (after memory) |
| dpt-product | Requirements | Feature planning |
| dpt-research | Best practices | Any research needed |
| dpt-arch | Architecture, ADRs | Design decisions |
| dpt-scrum | Task breakdown | Complex tasks |
| dpt-dev | Implementation | Coding |
| dpt-data | Database | Schema, queries |
| dpt-api | API design | Endpoints |
| dpt-ux | UI/UX | Interface design |
| dpt-sec | Security | Audits, vulnerability checks |
| dpt-lead | Code review | Quality checks |
| dpt-qa | Testing | Test coverage |
| dpt-review | Simplicity | Complexity checks |
| dpt-perf | Performance | Optimization (measure!) |
| dpt-ops | DevOps | CI/CD, deployment |
| dpt-docs | Documentation | Docs, README |
| dpt-grammar | Grammar | Text clarity |

## Parallel vs Sequential

**CAN be parallel (independent):**
```
dpt-sec + dpt-lead + dpt-qa + dpt-review + dpt-perf
```

**MUST be sequential:**
```
dpt-memory(START) → [work] → dpt-memory(END) → dpt-output
dpt-perf(baseline) → [change] → dpt-perf(measure)
```

## Memory Capture

### At Task End, Capture:

**Lessons** (what worked):
```yaml
lesson: "<what learned>"
context: "<when to apply>"
evidence: "<proof it works>"
```

**Mistakes** (what to avoid):
```yaml
mistake: "<what went wrong>"
root_cause: "<5 Whys result>"
prevention: "<how to avoid>"
```

**Patterns** (reusable solutions):
```yaml
pattern: "<name>"
problem: "<what it solves>"
solution: "<how to apply>"
```

## Learning Metrics

```
IMPROVING:    Prevented > New mistakes
STABLE:       Prevented = New mistakes  
NEEDS_ATTENTION: Prevented < New mistakes
```

## Output Format

Every task ends with:
```
MEMORY STATUS:
Project: <name>
Lessons: <n> (+<new>)
Mistakes: <n> (+<new>)
Prevented: <n>
Learning: Improving/Stable/Needs Attention
```

## 5 Whys (For Bug Fixes)

```
Problem: [Description]
Why 1: → Because...
Why 2: → Because...
Why 3: → Because...
Why 4: → Because...
Why 5: → ROOT CAUSE (fix this!)
```
</coding_guidelines>
