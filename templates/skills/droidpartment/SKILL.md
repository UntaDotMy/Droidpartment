---
name: droidpartment
description: 18 expert agents with memory system. Tracks lessons, mistakes, and learning progress.
---

# Droidpartment - 18 Experts + Memory

Coordinator-only. Agents do not call each other; the orchestrator sequences them and consumes their outputs.

## PDCA Task Flow (orchestrator-driven)

```
PLAN:   memory(START) → product → research → arch → scrum → api/data/ux specs
DO:     dev → ops (pipeline/secrets/health) → perf (baseline)
CHECK:  qa + lead + sec + review (+ perf re-measure)  # can run in parallel
ACT:    memory(END) → output
LOOP:   If any CHECK fails → record mistake → go back to PLAN with new lessons
```

Rules:
- memory(END) and output are always sequential.
- Agents stay independent: each consumes inputs (briefs/specs/memory) and emits findings/evidence; no cross-agent invocation.

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

## Parallel / Sequential Guidance
- Parallel-safe (CHECK phase): qa, lead, sec, review (+ docs/grammar) once artifacts exist; perf re-measure after build.
- Must be sequential: memory START → PLAN chain → perf baseline before change → memory END → output.

## Evidence & Memory Discipline
- Each agent: Before (retrieve relevant lessons/patterns/mistakes), Do (domain checklist, produce evidence), After (1–2 sentence lesson; if issue, include mistake+prevention; add tags).
- Keep memory entries concise; no logs/traces; shared project/global store.*** End Patch***");
