---
name: global-bug-sweep
description: Performs a comprehensive cross-cutting bug sweep after all tasks complete. Checks for integration issues, state problems, error handling, and forbidden patterns.
---

# Global Bug Sweep Skill

## When to Use
Invoke this skill after ALL implementation tasks are complete, before marking the work as done.

## Instructions

### 1. INTEGRATION ISSUES
Check all modified files for:
- All imports resolve correctly
- No circular dependencies introduced
- Type definitions align across files
- API contracts match between caller/callee
- Interface implementations complete

### 2. STATE & DATA FLOW
Verify:
- State mutations are intentional
- Data transformations preserve type safety
- Async operations properly awaited
- Race conditions addressed
- No dangling promises

### 3. ERROR HANDLING CONTINUITY
Confirm:
- Errors propagate correctly through layers
- Error types are consistent
- User-facing errors are meaningful
- No swallowed exceptions (catch (e) {})
- Resources cleaned up in finally blocks

### 4. CROSS-CUTTING PATTERNS
Validate:
- Logging is consistent across changes
- Authentication applied uniformly
- Validation patterns consistent
- Caching behavior aligned
- Naming conventions followed

### 5. FORBIDDEN PATTERNS SCAN

Run these checks on all modified files:

```bash
# TODO/FIXME check - should be empty
grep -rn "TODO\|FIXME\|XXX\|HACK" [modified files]

# Debug statements - should be empty
grep -rn "console\.log\|debugger\|print(" [modified files]

# Hardcoded values - review carefully
grep -rn "localhost\|127.0.0.1\|password.*=\|api_key.*=" [modified files]

# Commented code blocks - should not exist
[manual inspection for commented code]
```

### 6. OUTPUT FORMAT

```
═══════════════════════════════════════════════════════════════
GLOBAL BUG SWEEP RESULTS
═══════════════════════════════════════════════════════════════

Scope: [files modified in this session]
Status: [CLEAN / ISSUES_FOUND]

───────────────────────────────────────────────────────────────
INTEGRATION CHECKS
───────────────────────────────────────────────────────────────
[✓] Imports resolve correctly
[✓] No circular dependencies
[✓] Types align
[✓] API contracts match

───────────────────────────────────────────────────────────────
STATE & DATA FLOW
───────────────────────────────────────────────────────────────
[✓] Mutations intentional
[✓] Type safety preserved
[✓] Async handled properly
[✓] No race conditions

───────────────────────────────────────────────────────────────
ERROR HANDLING
───────────────────────────────────────────────────────────────
[✓] Errors propagate correctly
[✓] Consistent error types
[✓] No swallowed exceptions
[✓] Resources cleaned up

───────────────────────────────────────────────────────────────
FORBIDDEN PATTERNS
───────────────────────────────────────────────────────────────
[✓] No TODO/FIXME
[✓] No debug statements
[✓] No hardcoded secrets
[✓] No commented code

───────────────────────────────────────────────────────────────
ISSUES FOUND (if any)
───────────────────────────────────────────────────────────────
| # | Issue | Location | Severity |
|---|-------|----------|----------|
| 1 | [desc] | [file:line] | [H/M/L] |

───────────────────────────────────────────────────────────────
REMEDIATION
───────────────────────────────────────────────────────────────
[Actions taken to fix issues]

═══════════════════════════════════════════════════════════════
SWEEP COMPLETE: [PASSED / NEEDS_FIXES]
═══════════════════════════════════════════════════════════════
```

## Success Criteria
- All integration checks pass
- No forbidden patterns found
- All issues identified are documented
- Remediation applied for found issues
