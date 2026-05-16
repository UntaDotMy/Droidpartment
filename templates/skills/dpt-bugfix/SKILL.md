---
name: dpt-bugfix
description: Streamlined bug-fix workflow that runs dev + qa + sec audits without the heavyweight PRD/architecture phases. Use for fixing a specific bug, regression, or failing test where the scope is already understood.
---

# Bug fix workflow

Use this when the bug location is roughly known and a full PRD/architecture pass
would be overkill. Heavier than a one-line edit, lighter than the fullstack
playbook.

## Wave plan

```
Wave 1 [INIT]    Task(dpt-memory, "START: fix <bug>")

Wave 2 [DIAGNOSE] Task(dpt-dev, "investigate root cause of <bug>")
                  # If root cause is unclear after investigation, escalate to dpt-research.

Wave 3 [FIX]     Task(dpt-dev, "implement minimal fix + regression test")

Wave 4 [VERIFY]  Task(dpt-qa, "run the regression test, full suite, and any affected flows")
                 Task(dpt-sec, "ensure no security regression on the touched surface")
                 # parallel

Wave 5 [FINISH]  Task(dpt-memory, "END: <root cause>, <fix summary>")
                 Task(dpt-output, "summarize bug + fix")
```

## Quality bar

- Always add a failing test BEFORE the fix when possible. The test should fail
  on the current code and pass after the fix.
- Run the affected test file via `dpt run -- <test cmd>` so the agent context
  stays clean.
- If the fix touches an existing function used elsewhere, dpt-qa must run those
  call sites too.

## Skip when

- The "bug" is a missing feature -> use `dpt-fullstack`.
- The fix is one-line and obvious -> just edit + test, no waves needed.

## Output

Final report from dpt-output should include:

- Root cause (one sentence)
- Fix summary (one sentence)
- Files changed (list)
- Test added / updated
- Tokens saved by the compactor (from `dpt stats`, optional)
