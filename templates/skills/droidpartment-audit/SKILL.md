---
name: droidpartment-audit
description: Comprehensive code audit with parallel security, quality, and performance checks.
---

# Audit Workflow

Use this skill for comprehensive code audits across security, quality, and performance.

## When to Use

- Pre-release audits
- Security reviews
- Code quality assessments
- Performance evaluations
- "Review everything" requests

## Workflow

```
1. Task(dpt-memory, "START: audit [scope]")
2. PARALLEL:
   - Task(dpt-sec, "security audit [files]")
   - Task(dpt-lead, "code review [files]")
   - Task(dpt-qa, "test coverage [files]")
   - Task(dpt-perf, "performance check [files]")
   - Task(dpt-review, "simplicity check [files]")
3. Task(dpt-memory, "END: audit findings")
4. Task(dpt-output, "synthesize audit report")
```

## Audit Domains

| Agent | Focus | Standards |
|-------|-------|-----------|
| `dpt-sec` | Security | OWASP Top 10, CWE |
| `dpt-lead` | Quality | SOLID, Clean Code |
| `dpt-qa` | Testing | Test Pyramid |
| `dpt-perf` | Performance | Response time, memory |
| `dpt-review` | Simplicity | YAGNI, no over-engineering |

## Example

```javascript
Task(dpt-memory, "START: pre-release audit for auth module")

// Run in parallel
Task(dpt-sec, "security audit src/auth/")
Task(dpt-lead, "code review src/auth/")
Task(dpt-qa, "test coverage src/auth/")

Task(dpt-memory, "END: audit complete, 2 critical, 5 warnings")
Task(dpt-output, "format audit report with severity rankings")
```

## Report Format

```
Summary: Audit complete - X critical, Y warnings, Z info

Findings:
- CRITICAL: [issue] in [file] - [fix]
- WARNING: [issue] in [file] - [recommendation]
- INFO: [observation]

Follow-up:
- [ ] Address critical issues before release
- [ ] Schedule warning fixes for next sprint
```
