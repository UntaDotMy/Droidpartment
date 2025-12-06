<coding_guidelines>
# Droidpartment - 18 Expert Agents

Call specialists directly. Always use memory at start and end.

## Task Flow

```
START: dpt-memory (retrieve lessons)
  ↓
WORK: Call relevant experts (parallel or sequential)
  ↓
END: dpt-memory (capture lessons)
  ↓
OUTPUT: dpt-output (format with memory stats)
```

## The 18 Experts

| Expert | Specialty |
|--------|-----------|
| dpt-memory | Lessons, mistakes, knowledge tracking |
| dpt-sec | Security audits, OWASP |
| dpt-lead | Code review, best practices |
| dpt-qa | Testing, coverage |
| dpt-arch | Architecture, design patterns |
| dpt-dev | Implementation |
| dpt-review | Simplicity check |
| dpt-data | Database, queries |
| dpt-api | API design |
| dpt-ux | UI/UX, accessibility |
| dpt-docs | Documentation |
| dpt-perf | Performance |
| dpt-ops | DevOps, CI/CD |
| dpt-research | Best practices research |
| dpt-product | Requirements |
| dpt-scrum | Task breakdown |
| dpt-grammar | Text clarity |
| dpt-output | Format output with memory stats |

## Always Start with Memory

```
1. Call dpt-memory: "START - retrieve lessons for [task type] on [project]"
2. Apply lessons to your work
3. Do the task with relevant experts
4. Call dpt-memory: "END - capture what was learned"
5. Call dpt-output: "Format results with memory statistics"
```

## Example: Audit Task

```
1. dpt-memory: "START - retrieve lessons for audit"
   → Returns past lessons, mistakes to avoid

2. Parallel expert calls:
   - dpt-sec: security audit
   - dpt-lead: code review
   - dpt-qa: test coverage

3. dpt-memory: "END - learned: [findings], mistakes: [issues found]"
   → Saves to memory

4. dpt-output: "Format audit results with memory stats"
   → Shows learning curve, knowledge gained
```

## Memory Output Format

Every task should end with:
```
MEMORY STATUS:
Project: <name>
Lessons: <n> (+<new>)
Mistakes: <n> (+<new>)
Prevented: <n>
Learning: <Improving/Stable/Needs Attention>
```

## Parallel vs Sequential

Parallel (independent):
- dpt-sec + dpt-lead + dpt-qa (audit)

Sequential (dependent):
- dpt-memory → dpt-arch → dpt-dev → dpt-lead → dpt-qa → dpt-sec → dpt-memory → dpt-output
</coding_guidelines>
