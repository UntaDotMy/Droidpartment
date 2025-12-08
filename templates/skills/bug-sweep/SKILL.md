---
name: bug-sweep
description: Comprehensive bug sweep after implementation using dpt-qa and dpt-sec agents.
---

# Bug Sweep Skill

Use after implementation to catch integration issues, state problems, and forbidden patterns.

## When to Use

- After ALL implementation tasks complete
- Before marking work as done
- Pre-release verification

## Workflow

```javascript
Task(dpt-memory, "START: bug sweep for [scope]")
Task(dpt-qa, "integration and state verification")
Task(dpt-sec, "security and forbidden patterns check")
Task(dpt-review, "simplicity and error handling check")
Task(dpt-memory, "END: bug sweep complete")
Task(dpt-output, "summarize findings")
```

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
Summary: Bug sweep complete - X files scanned, Y issues found

Findings:
- ✅ Integration: All imports resolve, no circular deps
- ✅ State: Mutations intentional, async properly handled
- ✅ Errors: Propagation correct, no swallowed exceptions
- ⚠️ Forbidden: 1 TODO found in src/api.ts:45

Issues:
- HIGH: [issue] in [file:line] - [fix required]
- MEDIUM: [issue] in [file:line] - [recommendation]

Remediation:
- Fixed TODO in src/api.ts by implementing the feature
- No remaining issues

Follow-up:
- Status: PASSED / NEEDS_FIXES
```

## Success Criteria
- All integration checks pass
- No forbidden patterns found
- All issues identified are documented
- Remediation applied for found issues
