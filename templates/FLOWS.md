# Droidpartment Task Flows

Optimized workflows based on Agile, Scrum, PDCA, and industry best practices.

## Core Principles

### PDCA Learning Cycle (Applied to Every Task)
```
PLAN   → Retrieve lessons, define scope, identify risks
DO     → Execute with expert agents
CHECK  → Verify quality, compare to lessons
ACT    → Capture new lessons, update memory
```

### Memory Discipline
- **START**: Always retrieve relevant lessons before work
- **DURING**: Apply lessons, note deviations
- **END**: Capture what worked, what didn't, and why
- **LOOP**: If CHECK fails, go back to PLAN with new lessons

---

## Flow 1: Feature Development

**Use when**: Building new features, adding functionality

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN PHASE                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. dpt-memory: "START - feature development for [feature]" │
│    → Retrieve: past feature patterns, mistakes to avoid    │
│                                                             │
│ 2. dpt-product: Define user story + acceptance criteria    │
│    Format: "As a [user], I want [goal], so that [benefit]" │
│    Include: Definition of Ready (INVEST criteria)          │
│                                                             │
│ 3. dpt-research: Best practices for this type of feature   │
│    → Official docs, proven patterns                        │
│                                                             │
│ 4. dpt-arch: Design solution + ADR                         │
│    → Architecture Decision Record for significant choices  │
│                                                             │
│ 5. dpt-scrum: Break into subtasks with dependencies        │
│    → Identify parallel vs sequential work                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ DO PHASE                                                    │
├─────────────────────────────────────────────────────────────┤
│ 6. dpt-dev: Implement following existing patterns          │
│    → Small commits, tests alongside code                   │
│                                                             │
│ 7. dpt-data: Database changes (if needed)                  │
│    → Migrations, indexes, queries                          │
│                                                             │
│ 8. dpt-api: API endpoints (if needed)                      │
│    → OpenAPI spec, versioning                              │
│                                                             │
│ 9. dpt-ux: UI components (if needed)                       │
│    → Accessibility, responsive design                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CHECK PHASE (CAN BE PARALLEL)                               │
├─────────────────────────────────────────────────────────────┤
│ 10. dpt-qa: Test coverage + test pyramid balance           │
│     → Unit 70%, Integration 20%, E2E 10%                   │
│                                                             │
│ 11. dpt-lead: Code review (SOLID, clean code)              │
│     → Definition of Done checklist                         │
│                                                             │
│ 12. dpt-sec: Security audit (OWASP, CWE)                   │
│     → No new vulnerabilities introduced                    │
│                                                             │
│ 13. dpt-review: Simplicity check (YAGNI)                   │
│     → No over-engineering                                  │
│                                                             │
│ 14. dpt-perf: Performance impact                           │
│     → Measure before/after                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ACT PHASE                                                   │
├─────────────────────────────────────────────────────────────┤
│ IF CHECK PASSED:                                            │
│   15. dpt-docs: Update documentation                        │
│   16. dpt-memory: "END - capture lessons"                   │
│       → What worked, patterns discovered                   │
│   17. dpt-output: Format results with memory stats          │
│                                                             │
│ IF CHECK FAILED:                                            │
│   → Record mistake + prevention                            │
│   → Go back to PLAN with new lessons                       │
│   → Loop until CHECK passes                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow 2: Bug Fix

**Use when**: Fixing bugs, resolving issues

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN PHASE                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. dpt-memory: "START - bug fix for [issue]"                │
│    → Retrieve: similar past bugs, root causes              │
│                                                             │
│ 2. dpt-research: Reproduce + understand the bug            │
│    → Gather context, identify affected areas               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ DO PHASE                                                    │
├─────────────────────────────────────────────────────────────┤
│ 3. ROOT CAUSE ANALYSIS (5 Whys)                             │
│    Why 1: Why did the bug occur?                           │
│    Why 2: Why did that happen?                             │
│    Why 3: ...continue until root cause found               │
│                                                             │
│ 4. dpt-dev: Fix the root cause (not just symptom)          │
│    → Single focused fix, no scope creep                    │
│                                                             │
│ 5. dpt-qa: Write regression test FIRST                     │
│    → Test must fail before fix, pass after                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CHECK PHASE (PARALLEL)                                      │
├─────────────────────────────────────────────────────────────┤
│ 6. dpt-qa: Verify fix + run all tests                       │
│ 7. dpt-lead: Review fix (focused, no extras)               │
│ 8. dpt-sec: Security impact check                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ACT PHASE (BLAMELESS POSTMORTEM)                            │
├─────────────────────────────────────────────────────────────┤
│ 9. dpt-memory: "END - capture bug lesson"                   │
│    → Root cause, how to prevent, detection method          │
│    → Focus on SYSTEMS not blame                            │
│                                                             │
│ 10. dpt-output: Format with memory stats                    │
│     → Include: What to watch for in future                 │
└─────────────────────────────────────────────────────────────┘
```

**5 Whys Template:**
```
Problem: [Bug description]
Why 1: [First cause] → Because...
Why 2: [Deeper cause] → Because...
Why 3: [Deeper cause] → Because...
Why 4: [Deeper cause] → Because...
Why 5: [Root cause] → THIS is what we fix
```

---

## Flow 3: Research / Understanding

**Use when**: Learning codebase, exploring options, understanding systems

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN PHASE                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. dpt-memory: "START - research [topic]"                   │
│    → Retrieve: past research, known patterns               │
│                                                             │
│ 2. Define research questions:                               │
│    - What do we need to know?                              │
│    - Why do we need to know it?                            │
│    - How will we use this knowledge?                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ DO PHASE                                                    │
├─────────────────────────────────────────────────────────────┤
│ 3. dpt-research: Find authoritative sources                 │
│    Priority: Official docs > Standards > Academic > Blogs  │
│                                                             │
│ 4. dpt-arch: Analyze architecture/patterns found           │
│    → Document trade-offs, applicability                    │
│                                                             │
│ 5. Compare options (if multiple):                           │
│    | Option | Pros | Cons | Fit |                          │
│    |--------|------|------|-----|                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CHECK PHASE                                                 │
├─────────────────────────────────────────────────────────────┤
│ 6. Verify sources are authoritative                         │
│ 7. Cross-reference findings                                │
│ 8. dpt-review: Is this the simplest approach?              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ACT PHASE                                                   │
├─────────────────────────────────────────────────────────────┤
│ 9. dpt-memory: "END - capture research findings"            │
│    → Key learnings, sources, applicability                 │
│    → Store as reusable pattern if valuable                 │
│                                                             │
│ 10. dpt-output: Format findings with sources                │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow 4: Documentation

**Use when**: Writing docs, updating README, API docs

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN PHASE                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. dpt-memory: "START - documentation for [topic]"          │
│    → Retrieve: documentation patterns, style guides        │
│                                                             │
│ 2. Define audience and purpose:                             │
│    - Who will read this?                                   │
│    - What do they need to accomplish?                      │
│    - What do they already know?                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ DO PHASE                                                    │
├─────────────────────────────────────────────────────────────┤
│ 3. dpt-docs: Write documentation                            │
│    README: Project overview, quick start, usage            │
│    API: OpenAPI spec, request/response examples            │
│    ADR: Context, decision, consequences                    │
│                                                             │
│ 4. dpt-grammar: Check clarity and grammar                  │
│    → Active voice, simple words, short sentences           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CHECK PHASE                                                 │
├─────────────────────────────────────────────────────────────┤
│ 5. dpt-review: Is it simple enough?                         │
│    → Can a new person understand in 5 minutes?             │
│                                                             │
│ 6. Verify:                                                  │
│    - Code examples work (copy-paste test)                  │
│    - Links are valid                                       │
│    - No outdated information                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ACT PHASE                                                   │
├─────────────────────────────────────────────────────────────┤
│ 7. dpt-memory: "END - capture documentation lessons"        │
│    → What patterns worked, what was unclear                │
│                                                             │
│ 8. dpt-output: Format with memory stats                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow 5: Improvement / Refactoring

**Use when**: Improving code quality, refactoring, optimization

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN PHASE                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. dpt-memory: "START - improvement for [area]"             │
│    → Retrieve: past improvements, what worked              │
│                                                             │
│ 2. dpt-perf: MEASURE BASELINE FIRST                         │
│    → Never improve without measuring!                      │
│    → Document: current metrics, target metrics             │
│                                                             │
│ 3. dpt-review: Identify improvement opportunities           │
│    → Code smells, complexity, technical debt               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ DO PHASE (Kaizen - Small Incremental Changes)               │
├─────────────────────────────────────────────────────────────┤
│ 4. dpt-dev: Implement improvement                           │
│    → Small, focused changes                                │
│    → One improvement at a time                             │
│    → Keep tests passing throughout                         │
│                                                             │
│ 5. dpt-perf: MEASURE AFTER                                  │
│    → Compare to baseline                                   │
│    → Document improvement                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CHECK PHASE (PARALLEL)                                      │
├─────────────────────────────────────────────────────────────┤
│ 6. dpt-qa: All tests still pass                             │
│ 7. dpt-lead: Code review (better, not just different)      │
│ 8. dpt-sec: No security regressions                        │
│ 9. dpt-review: Actually simpler? (not just moved)          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ACT PHASE (Retrospective)                                   │
├─────────────────────────────────────────────────────────────┤
│ 10. dpt-memory: "END - capture improvement lessons"         │
│     → What improved, by how much                           │
│     → Pattern to reuse in future                           │
│                                                             │
│ 11. dpt-output: Format with before/after metrics            │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow 6: Audit / Review

**Use when**: Security audit, code review, quality check

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN PHASE                                                  │
├─────────────────────────────────────────────────────────────┤
│ 1. dpt-memory: "START - audit [project/area]"               │
│    → Retrieve: past audit findings, recurring issues       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ DO PHASE (ALL PARALLEL - Independent audits)                │
├─────────────────────────────────────────────────────────────┤
│ 2. dpt-sec: Security audit                                  │
│    → OWASP Top 10, CWE Top 25, dependency scan             │
│                                                             │
│ 3. dpt-lead: Code quality review                           │
│    → SOLID, clean code, technical debt                     │
│                                                             │
│ 4. dpt-qa: Test coverage analysis                          │
│    → Pyramid balance, anti-patterns                        │
│                                                             │
│ 5. dpt-review: Complexity check                            │
│    → Over-engineering, YAGNI violations                    │
│                                                             │
│ 6. dpt-perf: Performance baseline                          │
│    → Identify bottlenecks                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ CHECK PHASE                                                 │
├─────────────────────────────────────────────────────────────┤
│ 7. Consolidate findings                                     │
│ 8. Prioritize by severity/impact                           │
│ 9. Create action items                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ACT PHASE                                                   │
├─────────────────────────────────────────────────────────────┤
│ 10. dpt-memory: "END - capture audit findings"              │
│     → Issues found, patterns, prevention strategies        │
│                                                             │
│ 11. dpt-output: Format with prioritized action items        │
└─────────────────────────────────────────────────────────────┘
```

---

## Memory Capture Templates

### Lesson Template
```yaml
- id: lesson_<timestamp>
  date: <YYYY-MM-DD>
  type: <feature|bugfix|research|improvement|audit>
  lesson: "<1-2 sentence: what worked or what learned>"
  context: "<when to apply this lesson>"
  evidence: "<specific example that proves this>"
  tags: [<relevant tags>]
```

### Mistake Template
```yaml
- id: mistake_<timestamp>
  date: <YYYY-MM-DD>
  type: <feature|bugfix|research|improvement|audit>
  mistake: "<what went wrong>"
  root_cause: "<5 Whys result>"
  prevention: "<how to avoid in future>"
  detection: "<how to catch early>"
  tags: [<relevant tags>]
```

### Pattern Template
```yaml
- id: pattern_<timestamp>
  date: <YYYY-MM-DD>
  name: "<pattern name>"
  problem: "<what problem it solves>"
  solution: "<how to apply>"
  when_to_use: "<context>"
  when_not_to_use: "<anti-context>"
  success_count: <n>
  tags: [<relevant tags>]
```

---

## Retrospective Questions (End of Each Task)

### What Went Well?
- What lessons from memory helped?
- What new patterns discovered?
- What was efficient?

### What Didn't Go Well?
- What mistakes were made?
- What took longer than expected?
- What was confusing?

### What to Improve?
- What should we do differently next time?
- What new lesson should we capture?
- What pattern should we document?

---

## Learning Metrics

Track these to measure improvement:

| Metric | Good Trend |
|--------|------------|
| Mistakes prevented (from lessons) | ↑ Increasing |
| New mistakes per task | ↓ Decreasing |
| Lessons applied per task | ↑ Increasing |
| Time to complete similar tasks | ↓ Decreasing |
| Rework/iterations needed | ↓ Decreasing |

```
Learning Curve Status:
- IMPROVING: Prevented > New mistakes
- STABLE: Prevented = New mistakes
- NEEDS_ATTENTION: Prevented < New mistakes
```
