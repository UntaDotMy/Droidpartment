# Droidpartment

**18 Expert Agents for Factory AI** - Call specialists directly for security, code review, testing, architecture, and more.

## Installation

```bash
npm install -g droidpartment
droidpartment
```

Or one-time:
```bash
npx droidpartment
```

After install: `/settings` → Experimental → Enable Custom Droids → Restart CLI

## The 18 Experts

| Expert | Specialty |
|--------|-----------|
| dpt-memory | Learning system - retrieves past lessons, captures new knowledge |
| dpt-sec | Security audits, OWASP Top 10 |
| dpt-lead | Code review, best practices, SOLID |
| dpt-qa | Testing strategies, coverage |
| dpt-arch | Architecture, design patterns |
| dpt-dev | Implementation, coding |
| dpt-review | Simplicity check, anti-over-engineering |
| dpt-data | Database, schemas, queries |
| dpt-api | API design, REST, consistency |
| dpt-ux | UI/UX, accessibility |
| dpt-docs | Documentation |
| dpt-perf | Performance optimization |
| dpt-ops | DevOps, CI/CD, deployment |
| dpt-research | Best practices research |
| dpt-product | Requirements, user stories |
| dpt-scrum | Task breakdown, planning |
| dpt-grammar | Text clarity, grammar |
| dpt-output | Output formatting with memory stats |

## How to Use

Call experts directly with Task tool:

```
Task tool:
  subagent_type: "dpt-sec"
  prompt: "Audit security of this project"
```

### Parallel Calls (Independent Tasks)

For audits, call multiple experts at once:
- dpt-sec (security)
- dpt-lead (code quality)
- dpt-qa (test coverage)

### Sequential Calls (Dependent Tasks)

For features, call in order:
1. dpt-memory → retrieve past lessons
2. dpt-arch → design
3. dpt-dev → implement
4. dpt-lead → review
5. dpt-qa → test
6. dpt-sec → security check
7. dpt-memory → capture lessons learned

## Commands

| Command | Description |
|---------|-------------|
| `npx droidpartment` | Install or update |
| `npx droidpartment --memory` | Manage/clean memory |
| `npx droidpartment --uninstall` | Remove |

## Memory System

Experts learn over time - the system grows smarter with each session:

```
~/.factory/memory/
├── lessons.yaml     ← What worked (universal)
├── patterns.yaml    ← Successful patterns
├── mistakes.yaml    ← What to avoid
└── projects/
    └── {project}/   ← Project-specific knowledge
```

### Memory Flow
```
START: dpt-memory (retrieve lessons)
  ↓
WORK: Call relevant experts
  ↓
END: dpt-memory (capture lessons)
  ↓
OUTPUT: dpt-output (format with memory stats)
```

### Memory Stats
Every task ends with:
```
MEMORY STATUS:
Project: <name>
Lessons: <n> (+<new>)
Mistakes: <n> (+<new>)
Prevented: <n>
Learning: <Improving/Stable>
```

## Install Locations

| Location | Path | Use Case |
|----------|------|----------|
| Personal | `~/.factory/` | Works in ALL projects (recommended) |
| Project | `./.factory/` | Git-committable, team sharing |

## Philosophy

```
SIMPLE > COMPLEX
EXPERT > GENERALIST
PARALLEL > SEQUENTIAL (when possible)
LEARN FROM MISTAKES
```

## Version

3.0.1

## License

MIT
