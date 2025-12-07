<coding_guidelines>
# MANDATORY: Droidpartment Workflow

## STOP! READ THIS FIRST!

**You MUST use custom droids for ALL tasks. Do NOT code directly.**

If you are about to write code, STOP and call `dpt-dev` instead.
If you are about to create tests, STOP and call `dpt-qa` instead.
If you are about to review code, STOP and call `dpt-lead` instead.

---

## RULE 1: ALWAYS Start With Memory

**BEFORE doing ANY work, you MUST call:**

```
Task(
  subagent_type: "dpt-memory",
  prompt: "START - [task type] for [project name]"
)
```

**NO EXCEPTIONS. Even for "simple" tasks.**

---

## RULE 2: Classify Task and Follow Flow

| User Request Contains | Task Type | REQUIRED Flow |
|----------------------|-----------|---------------|
| "audit", "review", "check", "analyze" | AUDIT | memory → (sec + lead + qa + perf) → memory → output |
| "fix", "bug", "error", "broken" | BUG_FIX | memory → dev → qa → memory → output |
| "add", "create", "implement", "build" | FEATURE | memory → product → arch → scrum → dev → qa → sec → memory → output |
| "update", "change", "modify" | IMPLEMENTATION | memory → scrum → dev → lead → qa → memory → output |
| "research", "find", "learn", "understand" | RESEARCH | memory → research → memory → output |
| "document", "readme", "docs" | DOCUMENTATION | memory → docs → grammar → memory → output |

---

## RULE 3: NEVER Code Directly

❌ **WRONG - Do NOT do this:**
```javascript
// Main droid writing code directly
const cleanup = onValue(ref, callback);
useEffect(() => cleanup, []);
```

✅ **CORRECT - Call dpt-dev instead:**
```
Task(
  subagent_type: "dpt-dev",
  prompt: "Implement [specific requirement]. File: [path]. Follow existing patterns."
)
```

---

## RULE 4: NEVER Skip These Steps

| Step | When | Call |
|------|------|------|
| Memory START | FIRST thing, always | `dpt-memory: "START..."` |
| Task Breakdown | 3+ steps | `dpt-scrum: "Break down..."` |
| Implementation | Any coding | `dpt-dev: "Implement..."` |
| Code Review | After coding | `dpt-lead: "Review..."` |
| Testing | After implementation | `dpt-qa: "Test..."` |
| Security | New features | `dpt-sec: "Audit..."` |
| Memory END | LAST thing, always | `dpt-memory: "END..."` |
| Output | Before responding | `dpt-output: "Format..."` |

---

## RULE 5: Parallel vs Sequential

**CAN run parallel (independent):**
```
Task(dpt-sec, ...) 
Task(dpt-lead, ...)  ← Same time OK
Task(dpt-qa, ...)
```

**MUST run sequential (wait for each):**
```
Task(dpt-memory, "START...") → WAIT
Task(dpt-scrum, ...) → WAIT
Task(dpt-dev, ...) → WAIT
Task(dpt-memory, "END...") → WAIT
Task(dpt-output, ...) → LAST
```

---

## RULE 6: Memory END Must Include Results

When calling dpt-memory END, include what happened:

```
Task(
  subagent_type: "dpt-memory",
  prompt: "END - [task type] completed.
    LESSONS: [what worked]
    MISTAKES: [what went wrong]
    FIXED: [what was changed]"
)
```

---

## RULE 7: Output is ALWAYS Last

**dpt-output MUST be called AFTER dpt-memory END completes.**

```
Task(dpt-memory, "END...") → WAIT for completion
Task(dpt-output, "Format results...") → THEN call this
```

---

## The 18 Experts

| subagent_type | Use For |
|---------------|---------|
| `dpt-memory` | START and END of every task |
| `dpt-output` | Format final results (LAST) |
| `dpt-product` | Requirements, user stories |
| `dpt-research` | Find best practices |
| `dpt-arch` | Design, architecture decisions |
| `dpt-scrum` | Break down tasks |
| `dpt-dev` | **ALL code implementation** |
| `dpt-data` | Database work |
| `dpt-api` | API design |
| `dpt-ux` | UI/UX design |
| `dpt-sec` | Security audits |
| `dpt-lead` | Code review |
| `dpt-qa` | Testing |
| `dpt-review` | Simplicity check |
| `dpt-perf` | Performance |
| `dpt-ops` | DevOps, CI/CD |
| `dpt-docs` | Documentation |
| `dpt-grammar` | Text clarity |

---

## Example: User Says "Fix the bug in auth"

**Step 1: Classify** → BUG_FIX

**Step 2: Execute Flow**
```
1. Task(dpt-memory, "START - bug fix for auth")     ← WAIT
2. Task(dpt-dev, "Fix bug in auth: [details]")      ← WAIT  
3. Task(dpt-qa, "Test the auth fix")                ← WAIT
4. Task(dpt-memory, "END - auth bug fixed")         ← WAIT
5. Task(dpt-output, "Format bug fix results")       ← LAST
```

---

## Example: User Says "Add new feature X"

**Step 1: Classify** → FEATURE

**Step 2: Execute Flow**
```
1. Task(dpt-memory, "START - new feature X")        ← WAIT
2. Task(dpt-product, "Define requirements for X")   ← WAIT
3. Task(dpt-arch, "Design architecture for X")      ← WAIT
4. Task(dpt-scrum, "Break down feature X tasks")    ← WAIT
5. Task(dpt-dev, "Implement feature X")             ← WAIT
6. Task(dpt-qa, "Test feature X")                   ← Can parallel
7. Task(dpt-sec, "Security check for X")            ← with qa
8. Task(dpt-memory, "END - feature X complete")     ← WAIT
9. Task(dpt-output, "Format feature results")       ← LAST
```

---

## Checkpoint: Before Responding to User

Ask yourself:
- [ ] Did I call dpt-memory START first?
- [ ] Did I use dpt-dev for code (not code directly)?
- [ ] Did I call dpt-memory END with results?
- [ ] Did I call dpt-output last?

**If any answer is NO, you skipped the workflow. Go back and fix it.**

---

## Remember

1. **Memory FIRST** - Always start with dpt-memory
2. **Never code directly** - Use dpt-dev
3. **Memory LAST** - Always end with dpt-memory then dpt-output
4. **Capture lessons** - Include what worked and what didn't
</coding_guidelines>
