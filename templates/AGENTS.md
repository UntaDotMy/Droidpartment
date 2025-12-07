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

---

## TASK TRIGGERS (AUTOMATIC)

When user says FIX/BUG/ERROR:
  MUST call: dpt-memory -> dpt-dev -> dpt-qa -> dpt-memory -> dpt-output

When user says IMPLEMENT/ADD/CREATE/BUILD:
  MUST call: dpt-memory -> dpt-scrum -> dpt-dev -> dpt-qa -> dpt-memory -> dpt-output

When user says AUDIT/REVIEW/CHECK/ANALYZE:
  MUST call: dpt-memory -> (dpt-sec + dpt-lead + dpt-qa) -> dpt-memory -> dpt-output

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
Step 7: dpt-output ......... REQUIRED - Cannot skip

VIOLATION = FAILURE. Restart with correct sequence.

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
- Main droid: Task(dpt-output, "Format results")

---

## THE 18 EXPERTS

Use Task tool with subagent_type:

Memory and Output:
- dpt-memory: START and END of every task (MANDATORY)
- dpt-output: Format final results (MANDATORY LAST)

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

---

## HOW TO CALL DROIDS

Use Task tool (NOT Skill tool):

Task(
  subagent_type: "dpt-dev",
  description: "Implement feature",
  prompt: "Implement [specific requirement] in [file path]"
)

---

## REMEMBER

1. Memory FIRST - dpt-memory START before anything
2. NEVER code directly - dpt-dev writes ALL code
3. NEVER skip scrum - dpt-scrum for 3+ step tasks
4. Memory LAST - dpt-memory END then dpt-output
5. CHECKPOINT before every action
</coding_guidelines>
