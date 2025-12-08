---
name: droidpartment
description: Autonomous software development department with 18 expert agents. Use for ANY development task - from bug fixes to full systems.
---

# 🤖 Droidpartment - Your AI Development Department

**Read `~/.factory/AGENTS.md` for detailed agent documentation.**

This skill orchestrates 18 specialized AI agents for ANY software development task.

## ⚠️ CRITICAL: You MUST Use Droidpartment Agents

```
┌────────────────────────────────────────────────────────────┐
│  NEVER write code directly.                                │
│  ALWAYS use Task(subagent_type: "dpt-*", prompt: "...")    │
│  ALWAYS start with dpt-memory(START)                       │
│  ALWAYS end with dpt-memory(END) → dpt-output              │
└────────────────────────────────────────────────────────────┘
```

## 🎯 Auto-Route Based on Task Complexity

### 🟢 SIMPLE (bug fix, typo, rename, config change)
```javascript
Task(subagent_type: "dpt-memory", prompt: "START: [describe task]")
Task(subagent_type: "dpt-dev", prompt: "[implement fix]")
Task(subagent_type: "dpt-qa", prompt: "verify the fix works")
Task(subagent_type: "dpt-memory", prompt: "END: what we learned")
Task(subagent_type: "dpt-output", prompt: "summarize results")
```

### 🟡 MEDIUM (single feature, endpoint, component)
```javascript
Task(subagent_type: "dpt-memory", prompt: "START: [feature name]")
Task(subagent_type: "dpt-scrum", prompt: "break down into steps")
Task(subagent_type: "dpt-dev", prompt: "[implement feature]")
Task(subagent_type: "dpt-qa", prompt: "test feature")
Task(subagent_type: "dpt-memory", prompt: "END: lessons learned")
Task(subagent_type: "dpt-output", prompt: "summarize")
```

### 🔴 COMPLEX (new system, multi-component, full feature)
```javascript
// Wave 1: Initialize
Task(subagent_type: "dpt-memory", prompt: "START: [system name]")
Task(subagent_type: "dpt-research", prompt: "best practices for [tech]")

// Wave 2: Plan
Task(subagent_type: "dpt-product", prompt: "create PRD.md")

// Wave 3: Design
Task(subagent_type: "dpt-arch", prompt: "create ARCHITECTURE.md")

// Wave 4: Breakdown
Task(subagent_type: "dpt-scrum", prompt: "create STORIES.md")

// Wave 5: Implement (parallel)
Task(subagent_type: "dpt-dev", prompt: "[component 1]")
Task(subagent_type: "dpt-dev", prompt: "[component 2]")

// Wave 6: Audit (parallel)
Task(subagent_type: "dpt-qa", prompt: "test all")
Task(subagent_type: "dpt-sec", prompt: "security audit")
Task(subagent_type: "dpt-lead", prompt: "code review")

// Wave 7: Finalize
Task(subagent_type: "dpt-memory", prompt: "END: capture all lessons")
Task(subagent_type: "dpt-output", prompt: "final report")
```

## 👥 All 18 Agents

| Agent | Expertise | When to Use |
|-------|-----------|-------------|
| **dpt-memory** | Learning system | ALWAYS first (START) and near-last (END) |
| **dpt-output** | Report synthesis | ALWAYS the final step |
| **dpt-product** | PRD, requirements | Complex features needing spec |
| **dpt-arch** | Architecture | System design, patterns |
| **dpt-scrum** | Task breakdown | Break work into stories |
| **dpt-research** | Best practices | Need solutions |
| **dpt-dev** | Code implementation | Writing code |
| **dpt-qa** | Testing | Verify implementation |
| **dpt-sec** | Security audit | Security-sensitive code |
| **dpt-lead** | Code review | Quality standards |
| **dpt-review** | Simplicity check | Over-engineering |
| **dpt-perf** | Performance | Optimization |
| **dpt-data** | Database | Schema, queries |
| **dpt-api** | API design | REST endpoints |
| **dpt-ux** | UI/UX | Frontend design |
| **dpt-ops** | DevOps | CI/CD, deployment |
| **dpt-docs** | Documentation | README, guides |
| **dpt-grammar** | Writing quality | Text improvement |

## 🌊 Wave Execution Pattern

```
Wave 1 [INIT]:      [P] dpt-memory(START), [P] dpt-research
Wave 2 [PLAN]:      [S] dpt-product → PRD.md
Wave 3 [DESIGN]:    [S] dpt-arch → ARCHITECTURE.md  
Wave 4 [BREAKDOWN]: [S] dpt-scrum → STORIES.md
Wave 5 [IMPLEMENT]: [P] dpt-dev (per component)
Wave 6 [AUDIT]:     [P] dpt-qa, [P] dpt-sec, [P] dpt-lead
Wave 7 [FINALIZE]:  [S] dpt-memory(END), [S] dpt-output

[P] = Parallel (run simultaneously)
[S] = Sequential (wait for previous)
```

## 📁 Artifacts Location

All artifacts in project memory (NOT in user's project):
```
~/.factory/memory/projects/{project}/artifacts/
├── PRD.md           (from dpt-product)
├── ARCHITECTURE.md  (from dpt-arch)
└── STORIES.md       (from dpt-scrum)
```

## 🔄 Feedback Loop

If audit finds issues:
```
needs_revision: true
revision_agent: dpt-dev
revision_reason: "Security issue in auth"
```
→ dpt-dev fixes → audits re-run → max 3 revisions

## 💡 Examples

### Bug Fix
```javascript
Task(subagent_type: "dpt-memory", prompt: "START: fix login timeout bug")
Task(subagent_type: "dpt-dev", prompt: "fix timeout in auth/token.ts")
Task(subagent_type: "dpt-qa", prompt: "verify timeout is fixed")
Task(subagent_type: "dpt-memory", prompt: "END: fixed by increasing token expiry")
Task(subagent_type: "dpt-output", prompt: "summarize bug fix")
```

### New Feature
```javascript
Task(subagent_type: "dpt-memory", prompt: "START: add user profile page")
Task(subagent_type: "dpt-product", prompt: "create PRD for profile page")
Task(subagent_type: "dpt-arch", prompt: "design profile components")
Task(subagent_type: "dpt-dev", prompt: "implement profile page")
Task(subagent_type: "dpt-qa", prompt: "test profile functionality")
Task(subagent_type: "dpt-memory", prompt: "END: profile page complete")
Task(subagent_type: "dpt-output", prompt: "summarize implementation")
```
