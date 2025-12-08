---
name: droidpartment-fullstack
description: Full-stack development with wave execution, artifacts, and parallel agents.
---

# Full-Stack Wave Workflow

Use this skill for complex features that need full planning, architecture, and parallel execution.

## When to Use

- Building new features from scratch
- Multi-component systems (API + UI + DB)
- Team coordination on complex tasks
- When you need PRD, Architecture, and Stories documents

## Wave Execution Pattern

```
Wave 1 [INIT]:     
  [P] dpt-memory(START), [P] dpt-research
  
Wave 2 [PLAN]:     
  [S] dpt-product → creates PRD.md
  
Wave 3 [DESIGN]:   
  [S] dpt-arch → creates ARCHITECTURE.md
  
Wave 4 [BREAKDOWN]:
  [S] dpt-scrum → creates STORIES.md with [P]/[S] markers
  
Wave 5 [IMPLEMENT]:
  [P] dpt-dev(component1), [P] dpt-dev(component2), ...
  
Wave 6 [AUDIT]:    
  [P] dpt-qa, [P] dpt-sec, [P] dpt-lead, [P] dpt-perf
  
Wave 7 [FINALIZE]: 
  [S] dpt-memory(END) → dpt-output
```

## Topology: Star

```
                    ┌─────────────┐
                    │ Orchestrator│
                    │   (Droid)   │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ↓               ↓               ↓
     ┌──────────┐    ┌──────────┐    ┌──────────┐
     │  Agent 1 │    │  Agent 2 │    │  Agent 3 │
     └──────────┘    └──────────┘    └──────────┘
```

## Workflow

```javascript
// Wave 1: Initialize
Task(dpt-memory, "START: full-stack [feature]")
Task(dpt-research, "find best practices for [tech stack]")

// Wave 2: Plan (artifact: ~/.factory/memory/projects/{project}/artifacts/PRD.md)
Task(dpt-product, "create PRD.md for [feature]")

// Wave 3: Design (artifact: ~/.factory/memory/projects/{project}/artifacts/ARCHITECTURE.md)
Task(dpt-arch, "read PRD.md, create ARCHITECTURE.md")

// Wave 4: Breakdown (artifact: ~/.factory/memory/projects/{project}/artifacts/STORIES.md)
Task(dpt-scrum, "read PRD.md + ARCHITECTURE.md, create STORIES.md")

// Wave 5: Implement (parallel per story)
// Droid reads STORIES.md and calls dpt-dev for each [P] story

// Wave 6: Audit (parallel)
Task(dpt-qa, "verify implementation against acceptance criteria")
Task(dpt-sec, "security audit of new code")
Task(dpt-lead, "code review for patterns and quality")

// Wave 7: Finalize
Task(dpt-memory, "END: capture lessons, patterns, mistakes")
Task(dpt-output, "synthesize all results into final report")
```

## Artifacts Created

All artifacts stored in project memory (NOT in user's project):

| Artifact | Agent | Location |
|----------|-------|----------|
| PRD.md | dpt-product | ~/.factory/memory/projects/{project}/artifacts/PRD.md |
| ARCHITECTURE.md | dpt-arch | ~/.factory/memory/projects/{project}/artifacts/ARCHITECTURE.md |
| STORIES.md | dpt-scrum | ~/.factory/memory/projects/{project}/artifacts/STORIES.md |

## Feedback Loop

If any audit agent finds issues:

```
needs_revision: true
revision_reason: "Security vulnerability in auth module"
revision_agent: dpt-dev
```

This triggers:
1. dpt-dev fixes the issue
2. Audit agents re-run
3. Loop until approved (max 3 revisions)

## Example

```javascript
// User: "Build a user authentication system with JWT"

// Wave 1
Task(dpt-memory, "START: auth system with JWT")
Task(dpt-research, "JWT best practices, refresh tokens, security")

// Wave 2
Task(dpt-product, "create PRD.md for auth system")
// Creates: .factory/artifacts/PRD.md

// Wave 3
Task(dpt-arch, "design auth architecture from PRD.md")
// Creates: .factory/artifacts/ARCHITECTURE.md

// Wave 4
Task(dpt-scrum, "break down auth into stories")
// Creates: .factory/artifacts/STORIES.md
// Stories: [P] auth middleware, [P] login endpoint, [S] refresh flow

// Wave 5
// Parallel implementation per story

// Wave 6
// Parallel audits

// Wave 7
Task(dpt-memory, "END: auth complete, lessons captured")
Task(dpt-output, "final report")
```

## Output Format

```
Summary: Full-stack development complete - 6 waves, 4 agents parallel

Artifacts:
- PRD.md: 5 user stories defined
- ARCHITECTURE.md: 3 components designed
- STORIES.md: 8 tasks (5 parallel, 3 sequential)

Waves Completed:
- Wave 1: Init ✓
- Wave 2: Plan ✓
- Wave 3: Design ✓
- Wave 4: Breakdown ✓
- Wave 5: Implement ✓
- Wave 6: Audit ✓ (1 revision)
- Wave 7: Finalize ✓

Revisions: 1 (security fix in auth)

Follow-up:
- next_agent: null (complete)
- confidence: 95
```
