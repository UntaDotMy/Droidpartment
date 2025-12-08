---
name: droidpartment
description: Coordinate 18 expert agents with wave execution, artifacts, and PDCA learning.
---

# Droidpartment Orchestration

Use this skill to coordinate 18 expert agents for development tasks.

## When to Use

- **Any development task** - Simple or complex
- **Multi-domain tasks** - code + tests + docs + security
- **Tasks requiring learning** - Memory captures lessons

## All 18 Agents

| Domain | Agent | Expertise |
|--------|-------|-----------|
| **Memory** | `dpt-memory` | Learning, lessons, patterns (START/END) |
| **Output** | `dpt-output` | Final report synthesis (ALWAYS LAST) |
| **Planning** | `dpt-product` | PRD.md, requirements, user stories |
| **Planning** | `dpt-scrum` | Task breakdown, [P]/[S] markers, waves |
| **Design** | `dpt-arch` | ARCHITECTURE.md, patterns, components |
| **Design** | `dpt-api` | REST endpoints, schemas, OpenAPI |
| **Design** | `dpt-data` | Database schemas, queries, migrations |
| **Design** | `dpt-ux` | UI/UX, accessibility, components |
| **Code** | `dpt-dev` | Implementation, tests, best practices |
| **Research** | `dpt-research` | Multi-hop research, official docs |
| **Quality** | `dpt-qa` | Testing, coverage, verification |
| **Quality** | `dpt-sec` | OWASP, security audit |
| **Quality** | `dpt-perf` | Performance, optimization |
| **Review** | `dpt-lead` | Code review, standards |
| **Review** | `dpt-review` | Simplicity, over-engineering check |
| **Docs** | `dpt-docs` | Documentation, READMEs |
| **Docs** | `dpt-grammar` | Writing quality, clarity |
| **Ops** | `dpt-ops` | CI/CD, Docker, deployment |

## Simple Task Flow

```javascript
Task(dpt-memory, "START: [task]")
Task(dpt-dev, "[implement]")
Task(dpt-qa, "[verify]")
Task(dpt-memory, "END: [lessons]")
Task(dpt-output, "summarize")
```

## Complex Task Flow (Waves)

```javascript
// Wave 1: Init
Task(dpt-memory, "START: [feature]")
Task(dpt-research, "[best practices]")

// Wave 2: Plan
Task(dpt-product, "create PRD.md")

// Wave 3: Design
Task(dpt-arch, "create ARCHITECTURE.md")

// Wave 4: Breakdown
Task(dpt-scrum, "create STORIES.md with [P]/[S]")

// Wave 5: Implement (parallel per [P] story)
Task(dpt-dev, "[component 1]")
Task(dpt-dev, "[component 2]")

// Wave 6: Audit (parallel)
Task(dpt-qa, "[test]")
Task(dpt-sec, "[security]")
Task(dpt-lead, "[review]")

// Wave 7: Finalize
Task(dpt-memory, "END: [lessons]")
Task(dpt-output, "synthesize")
```

## Parallel Audits

These ALWAYS run in parallel:
```javascript
Task(dpt-qa, "...")    // [P]
Task(dpt-sec, "...")   // [P]
Task(dpt-lead, "...")  // [P]
Task(dpt-perf, "...")  // [P]
Task(dpt-review, "...") // [P]
```

## Artifacts (in project memory)

| Artifact | Agent | Path |
|----------|-------|------|
| PRD.md | dpt-product | ~/.factory/memory/projects/{project}/artifacts/ |
| ARCHITECTURE.md | dpt-arch | ~/.factory/memory/projects/{project}/artifacts/ |
| STORIES.md | dpt-scrum | ~/.factory/memory/projects/{project}/artifacts/ |

## Example: Auth Feature

```javascript
Task(dpt-memory, "START: JWT authentication")
Task(dpt-research, "JWT best practices, refresh tokens")
Task(dpt-product, "create PRD.md for auth")
Task(dpt-arch, "design auth architecture")
Task(dpt-scrum, "break down into stories")
Task(dpt-dev, "implement auth middleware")
Task(dpt-dev, "implement login endpoint")
Task(dpt-qa, "test auth flows")
Task(dpt-sec, "security audit")
Task(dpt-memory, "END: auth complete")
Task(dpt-output, "final report")
```
