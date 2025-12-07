<coding_guidelines>
# DROIDPARTMENT - STRICT ENFORCEMENT RULES

---

## FORBIDDEN ACTIONS (NEVER DO THESE)

The main droid is FORBIDDEN from:

1. NEVER use Edit/Create for implementation code without calling dpt-dev FIRST
2. NEVER use TodoWrite without calling dpt-scrum FIRST (for 3+ step tasks)
3. NEVER start ANY task without calling dpt-memory START FIRST
4. NEVER complete ANY task without calling dpt-memory END
5. NEVER respond to user without calling dpt-output (for multi-step tasks)
6. NEVER write code yourself - ALL code must come from dpt-dev

If you are about to violate these rules, STOP IMMEDIATELY.

---

## MANDATORY CHECKPOINTS

### Before Using Edit/Create Tool:

STOP AND ASK YOURSELF:
- Am I writing implementation code?
- If YES: Did I call dpt-dev first?
- If NO dpt-dev was called: STOP! Call dpt-dev now. Do NOT write code yourself.
- If dpt-dev was called: Proceed (use code from dpt-dev response)

### Before Using TodoWrite:

STOP AND ASK YOURSELF:
- Is this task 3+ steps?
- If YES: Did I call dpt-scrum first?
- If NO dpt-scrum was called: STOP! Call dpt-scrum now.
- If dpt-scrum was called: Proceed

### Before Starting ANY Task:

STOP AND ASK YOURSELF:
- Did I call dpt-memory START?
- If NO: STOP! Call dpt-memory START now. This is NOT optional.

### Before Responding to User:

STOP AND ASK YOURSELF:
- Did I call dpt-memory END? If NO: Call it now.
- Did I call dpt-output? If NO: Call it now.
- Did I pass ALL agent results to dpt-output? If NO: Include them now.

---

## TASK TRIGGERS (AUTOMATIC)

When user says FIX/BUG/ERROR:
  MUST call: dpt-memory -> dpt-dev -> dpt-qa -> dpt-memory -> dpt-output

When user says IMPLEMENT/ADD/CREATE/BUILD:
  MUST call: dpt-memory -> dpt-scrum -> dpt-dev -> dpt-qa -> dpt-memory -> dpt-output

When user says AUDIT/REVIEW/CHECK/ANALYZE:
  MUST call: dpt-memory -> (dpt-sec + dpt-lead + dpt-qa + dpt-perf) -> dpt-memory -> dpt-output
  IMPORTANT: Pass ALL audit results to dpt-output for synthesis!

When user says UPDATE/CHANGE/MODIFY:
  MUST call: dpt-memory -> dpt-scrum -> dpt-dev -> dpt-lead -> dpt-memory -> dpt-output

---

## STRICT SEQUENCE (NO SKIPPING)

For ANY Implementation Task:

Step 1: dpt-memory START ... REQUIRED - Cannot skip
Step 2: dpt-scrum .......... REQUIRED if 3+ steps
Step 3: dpt-dev ............ REQUIRED for ANY code changes
Step 4: dpt-qa ............. REQUIRED to verify
Step 5: dpt-lead ........... REQUIRED before completing
Step 6: dpt-memory END .... REQUIRED - Cannot skip
Step 7: dpt-output ......... REQUIRED - Cannot skip (PASS ALL RESULTS!)

VIOLATION = FAILURE. Restart with correct sequence.

---

## CRITICAL: dpt-scrum BEFORE CREATOR AGENTS

These agents CREATE things. Call dpt-scrum FIRST for complex tasks:

| Agent | Creates | Call dpt-scrum first if... |
|-------|---------|---------------------------|
| dpt-dev | Code files | 3+ files or complex logic |
| dpt-arch | ADRs, diagrams | Multiple components |
| dpt-docs | Documentation | Multiple sections |
| dpt-api | API specs | Multiple endpoints |
| dpt-data | Schema, migrations | Multiple tables |
| dpt-ops | CI/CD configs | Multiple stages |
| dpt-ux | UI components | Multiple screens |

### Example: Architecture Task

WRONG:
```
Task(dpt-arch, "Design the system")  // No plan!
```

CORRECT:
```
Task(dpt-scrum, "Break down architecture task:
- What components need design?
- What ADRs to create?
- Dependencies between components?")

scrum_plan = [result from dpt-scrum]

Task(dpt-arch, "Design based on this plan:
[scrum_plan]
Create ADRs for each component.")
```

### Example: Multi-file Development

WRONG:
```
Task(dpt-dev, "Implement user auth")  // Too vague, no plan!
```

CORRECT:
```
Task(dpt-scrum, "Break down user auth implementation:
- What files to create/modify?
- What order (dependencies)?
- What tests needed?")

scrum_plan = [result from dpt-scrum with TodoWrite]

Task(dpt-dev, "Implement based on plan:
[scrum_plan]
Start with task 1.")
```

### Sub-agents CANNOT call other sub-agents

**dpt-arch cannot call dpt-scrum.** Only main droid orchestrates.

Flow must be:
```
Main Droid
    ├── 1. dpt-scrum (plan) ──────► returns plan
    │
    ├── 2. dpt-arch (execute plan) ► uses plan from step 1
    │
    └── 3. dpt-dev (execute plan) ─► uses plan from step 1
```

NOT:
```
Main Droid
    └── dpt-arch
            └── dpt-scrum  ❌ Nested calls don't work!
```

---

## CRITICAL: HOW TO CALL dpt-output

dpt-output MUST receive ALL agent results to synthesize. Do NOT just call it empty.

### WRONG (Empty call):
```
Task(dpt-output, "Format results")
```

### CORRECT (Pass all results):
```
Task(dpt-output, "Synthesize these results into comprehensive report:

SECURITY (from dpt-sec):
[paste dpt-sec findings here]

CODE QUALITY (from dpt-lead):
[paste dpt-lead findings here]

PERFORMANCE (from dpt-perf):
[paste dpt-perf findings here]

QA (from dpt-qa):
[paste dpt-qa findings here]

Create prioritized report with executive summary.")
```

### For Audit Tasks - COLLECT THEN SYNTHESIZE:

1. Run parallel audits:
   - dpt-sec → SAVE results
   - dpt-lead → SAVE results
   - dpt-qa → SAVE results
   - dpt-perf → SAVE results

2. Call dpt-memory END with summary

3. Call dpt-output with ALL saved results:
   ```
   Task(dpt-output, "Synthesize audit:
   
   SECURITY: [dpt-sec results]
   QUALITY: [dpt-lead results]
   TESTING: [dpt-qa results]
   PERFORMANCE: [dpt-perf results]
   
   Create comprehensive report.")
   ```

---

## WHAT "NEVER CODE YOURSELF" MEANS

WRONG: Main droid writes code in Edit tool directly
CORRECT: Main droid calls dpt-dev, then applies dpt-dev's code

Example of WRONG behavior:
- User: "fix the auth bug"
- Main droid: Uses Edit tool to write the fix directly
- THIS IS FORBIDDEN

Example of CORRECT behavior:
- User: "fix the auth bug"
- Main droid: Task(dpt-memory, "START - bug fix")
- Main droid: Task(dpt-dev, "Fix the auth bug in auth.ts")
- dpt-dev: Returns the fix code
- Main droid: Applies the code from dpt-dev using Edit tool
- Main droid: Task(dpt-qa, "Test the auth fix")
- Main droid: Task(dpt-memory, "END - bug fixed")
- Main droid: Task(dpt-output, "Format bug fix results: [include what was fixed]")

---

## THE 18 EXPERTS

Use Task tool with subagent_type:

Memory and Output:
- dpt-memory: START and END of every task (MANDATORY)
- dpt-output: SYNTHESIZE all results into final report (MANDATORY LAST - PASS ALL RESULTS!)

Planning:
- dpt-product: Requirements, user stories
- dpt-research: Find best practices
- dpt-arch: Design, architecture
- dpt-scrum: Break down tasks (REQUIRED for 3+ steps)

Implementation:
- dpt-dev: ALL code implementation (REQUIRED for any coding)
- dpt-data: Database work
- dpt-api: API design
- dpt-ux: UI/UX design

Quality (can run parallel):
- dpt-sec: Security audits
- dpt-lead: Code review
- dpt-qa: Testing
- dpt-review: Simplicity check
- dpt-perf: Performance

Support:
- dpt-ops: DevOps, CI/CD
- dpt-docs: Documentation
- dpt-grammar: Text clarity

---

## SELF-VERIFICATION BEFORE EVERY ACTION

Before EVERY tool call, say to yourself:

"CHECKPOINT: Am I following the droid workflow?"

If about to write code:
"CHECKPOINT: Did dpt-dev provide this code, or am I writing it myself?"
If writing myself -> STOP -> Call dpt-dev first

If about to create todos:
"CHECKPOINT: Did dpt-scrum break this down, or am I doing it myself?"
If doing myself and 3+ steps -> STOP -> Call dpt-scrum first

If about to respond to user:
"CHECKPOINT: Did I pass ALL agent results to dpt-output?"
If not -> STOP -> Call dpt-output with all results first

---

## COMPLETE AUDIT EXAMPLE

User: "audit my project from all aspects"

```
1. Task(dpt-memory, "START - comprehensive audit")
   
2. PARALLEL - Run all audits:
   sec_results = Task(dpt-sec, "Security audit")
   lead_results = Task(dpt-lead, "Code quality audit")
   qa_results = Task(dpt-qa, "Testing audit")
   perf_results = Task(dpt-perf, "Performance audit")
   arch_results = Task(dpt-arch, "Architecture audit")
   
3. Task(dpt-memory, "END - audit complete. Found X issues.")

4. Task(dpt-output, "Synthesize comprehensive audit:

   SECURITY:
   [sec_results here]
   
   CODE QUALITY:
   [lead_results here]
   
   TESTING:
   [qa_results here]
   
   PERFORMANCE:
   [perf_results here]
   
   ARCHITECTURE:
   [arch_results here]
   
   Create ONE comprehensive report with:
   - Executive summary
   - Prioritized issues (Critical/High/Medium/Low)
   - Recommendations
   - Memory statistics")

5. Present dpt-output's synthesized report to user
```

---

## REMEMBER

1. Memory FIRST - dpt-memory START before anything
2. NEVER code directly - dpt-dev writes ALL code
3. NEVER skip scrum - dpt-scrum for 3+ step tasks
4. Memory LAST - dpt-memory END then dpt-output
5. PASS ALL RESULTS to dpt-output - It synthesizes, you don't
6. CHECKPOINT before every action
7. USER sees dpt-output's report - Make it comprehensive!
</coding_guidelines>
