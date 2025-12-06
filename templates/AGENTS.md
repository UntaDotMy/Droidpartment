# Droidpartment v2.0 - Autonomous Software Development Department

## CRITICAL RULE

**For EVERY task, ALWAYS use the Task tool to delegate to subagent `dpt-chief` first.**

dpt-chief is the team leader who orchestrates 18 specialized agents with a real department workflow.

## How to Delegate

```
Task tool → subagent_type: "dpt-chief" → pass user's request
```

## Example

User: "Add login feature"
You: Call Task tool with subagent_type="dpt-chief", prompt="User wants to add login feature. Take ownership and deliver."

## Department Workflow (v2.0)

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

## PDCA Cycle (Continuous Improvement)

Every task follows Plan-Do-Check-Act:
- **PLAN**: Memory + Research + Architecture
- **DO**: Dev → Lead → QA (with back-and-forth)
- **CHECK**: Security + Review validation
- **ACT**: Capture lessons to memory (ALWAYS)

## Memory System (Grows Smarter Over Time)

```
~/.factory/memory/
├── lessons.yaml    ← Universal lessons
├── patterns.yaml   ← Successful patterns
├── mistakes.yaml   ← Mistakes to prevent
└── projects/       ← Per-project knowledge
```

Over time: Fewer mistakes, faster solutions, smarter predictions.

## Available Subagents (19 Total)

| Agent | Purpose |
|-------|---------|
| dpt-chief | Team leader (ALWAYS call first) |
| dpt-memory | Learning system (start + end) |
| dpt-research | Official docs research |
| dpt-dev | Implementation |
| dpt-arch | Architecture |
| dpt-qa | Testing |
| dpt-sec | Security |
| dpt-ops | DevOps |
| dpt-lead | Code review |
| dpt-docs | Documentation |
| dpt-data | Database |
| dpt-perf | Performance |
| dpt-ux | UI/UX |
| dpt-api | API design |
| dpt-grammar | Grammar check |
| dpt-review | Anti-over-engineering |
| dpt-output | Output formatting |
| dpt-scrum | Task breakdown |
| dpt-product | Requirements |

## Rules

1. ALWAYS delegate to dpt-chief first
2. Agents pass knowledge to each other
3. Development loop: Dev → Lead → QA (back-and-forth)
4. ALWAYS capture to memory after every task
5. Simple > Complex
