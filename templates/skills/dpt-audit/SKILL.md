---
name: dpt-audit
description: Parallel audit pass across security, performance, code quality, and simplicity. Use when the user asks for a code review, security audit, readiness review, or pre-release check on a branch or PR.
---

# Audit workflow

Run the five review specialists in parallel to produce a single combined report.

## Wave plan

```
Wave 1 [INIT]    Task(dpt-memory, "START: audit <branch / scope>")

Wave 2 [AUDIT]   Task(dpt-sec,    "OWASP / CWE audit on <scope>")
                 Task(dpt-lead,   "SOLID / architecture review on <scope>")
                 Task(dpt-qa,     "test coverage and runtime verification on <scope>")
                 Task(dpt-perf,   "performance review on <scope>")
                 Task(dpt-review, "simplicity / over-engineering check on <scope>")
                 # all parallel - none depend on each other

Wave 3 [FIX?]    # only if any audit reports needs_revision: true
                 Task(dpt-dev, "address audit findings: <bullets>")
                 # then re-run the failing audit lanes

Wave 4 [FINISH]  Task(dpt-memory, "END: <findings>")
                 Task(dpt-output, "combined audit report with severity ranking")
```

## Severity ranking

The combined report should sort findings by severity:

- **Critical** - data exposure, RCE, broken auth, broken access control
- **High** - injection, missing validation, broken business logic
- **Medium** - missing tests, code smells, perf cliff edges
- **Low** - style, micro-perf, doc gaps

## Token-efficiency notes

Audits read code, they do not write code. Run all five audit lanes in parallel
(Wave 2). The compactor will keep test/lint/grep output small for any sub-droid
that runs verification commands.

## Verdict rules

- If every audit lane returns `needs_revision: false`, the combined verdict is **APPROVED**.
- If any lane returns `needs_revision: true` after the 3-round revision cap, the combined verdict is **NEEDS REVISION** and routing back to the user is mandatory.
- A lane that hits the cap surfaces in the final `dpt-output` report as **action required** with the failure reason and the unresolved finding count.

## When to revise

If any audit emits `needs_revision: true` plus a `revision_reason`, route back
to dpt-dev for one revision pass, then re-run only the failing audit lane.
Cap at three revision rounds and escalate to the user if still red.

## Skip when

- The branch is a docs-only change.
- The scope is a one-line config tweak.
- The user explicitly asks for a single specialist (e.g., "just security").
