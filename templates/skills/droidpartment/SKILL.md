---
name: droidpartment
description: 18 expert agents with memory system. Tracks lessons, mistakes, and learning progress.
---

# Droidpartment - 18 Experts + Memory

Always use memory at start and end of tasks.

## Task Flow

```
1. START: dpt-memory (get lessons)
2. WORK: Call experts
3. END: dpt-memory (save lessons)
4. OUTPUT: dpt-output (show stats)
```

## The Experts

| Expert | Role |
|--------|------|
| dpt-memory | Lessons & learning stats |
| dpt-sec | Security |
| dpt-lead | Code review |
| dpt-qa | Testing |
| dpt-arch | Architecture |
| dpt-dev | Implementation |
| dpt-review | Simplicity |
| dpt-data | Database |
| dpt-api | API design |
| dpt-ux | UI/UX |
| dpt-docs | Documentation |
| dpt-perf | Performance |
| dpt-ops | DevOps |
| dpt-research | Research |
| dpt-product | Requirements |
| dpt-scrum | Task breakdown |
| dpt-grammar | Grammar |
| dpt-output | Format + stats |

## Memory System

```
~/.factory/memory/
├── lessons.yaml     ← What worked
├── mistakes.yaml    ← What to avoid
├── patterns.yaml    ← Successful patterns
├── stats.yaml       ← Learning progress
└── projects/        ← Per-project memory
```

## Output Format

End every task with:
```
MEMORY STATUS:
Project: <name>
Lessons: <n> (+<new>)
Mistakes: <n> (+<new>)
Prevented: <n>
Learning: Improving/Stable/Needs Attention
```

## Example

```
1. dpt-memory: "START - audit task"
2. dpt-sec + dpt-lead + dpt-qa (parallel)
3. dpt-memory: "END - save findings"
4. dpt-output: "Format with stats"
```
