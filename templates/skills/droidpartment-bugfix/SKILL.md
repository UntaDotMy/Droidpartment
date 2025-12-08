---
name: droidpartment-bugfix
description: Fix bugs with root cause analysis, regression testing, and learning capture.
---

# Bug Fix Workflow

Use this skill when fixing bugs to ensure proper root cause analysis and regression prevention.

## When to Use

- Bug reports
- Error fixes
- Regression issues
- "It's broken" requests

## Workflow

```
1. Task(dpt-memory, "START: bugfix [issue]")
2. Task(dpt-research, "reproduce and analyze [bug]")
3. Task(dpt-dev, "fix [root cause] in [file]")
4. Task(dpt-qa, "verify fix + regression test")
5. Task(dpt-memory, "END: fixed [issue], prevent [cause]")
6. Task(dpt-output, "summarize fix")
```

## Root Cause Analysis

Use 5 Whys method:
1. Why did it fail? → [symptom]
2. Why? → [intermediate cause]
3. Why? → [deeper cause]
4. Why? → [root cause]
5. Why? → [systemic issue]

## Example

```javascript
// User: "Login is broken"
Task(dpt-memory, "START: bugfix login failure")
Task(dpt-research, "reproduce login bug, find error logs")
// Findings: Token validation failing due to expired key
Task(dpt-dev, "fix token validation in src/auth/token.ts")
Task(dpt-qa, "verify login works + add regression test")
Task(dpt-memory, "END: fixed token validation, add key rotation reminder")
Task(dpt-output, "summarize login fix")
```

## Quality Gates

- [ ] Root cause identified (not just symptom)
- [ ] Fix addresses root cause
- [ ] Regression test added
- [ ] No new issues introduced
- [ ] Lesson captured in memory
