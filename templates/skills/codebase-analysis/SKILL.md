---
name: codebase-analysis
description: Analyzes and understands a codebase structure, patterns, conventions, and architecture. Use when starting work on a new project or understanding existing code.
---

# Codebase Analysis Skill

## When to Use
- Starting work on an unfamiliar project
- User asks to "understand the codebase"
- Before making significant changes
- When patterns/conventions are unclear

## Instructions

### PHASE 1: STRUCTURE DISCOVERY

1. List all directories and key files
2. Identify project type (web, api, cli, library, monorepo)
3. Find configuration files:
   - package.json / pyproject.toml / Cargo.toml / go.mod
   - tsconfig.json / .eslintrc / .prettierrc
   - Dockerfile / docker-compose.yml
   - CI/CD configs (.github/workflows, .gitlab-ci.yml)
4. Map the folder structure

### PHASE 2: TECHNOLOGY STACK

Identify:
- Language(s) and version(s)
- Framework(s) and version(s)
- Key dependencies and purposes
- Dev dependencies (testing, linting, building)
- Build/deploy tools

### PHASE 3: PATTERN ANALYSIS

Document:
- Code organization patterns
- Naming conventions (files, functions, classes)
- Import/export patterns
- Error handling patterns
- Testing patterns and frameworks

### PHASE 4: ARCHITECTURE MAPPING

Identify:
- Entry points (main files, API routes)
- Core modules and responsibilities
- Data flow
- State management approach
- API structure (if applicable)
- Database/storage patterns

### PHASE 5: CONVENTIONS EXTRACTION

Document for AGENTS.md:
- Build commands
- Test commands
- Lint commands
- File naming patterns
- Code style rules
- Git workflow (if visible)

## Output Format

```
╔══════════════════════════════════════════════════════════════╗
║               CODEBASE ANALYSIS REPORT                        ║
╠══════════════════════════════════════════════════════════════╣

📁 PROJECT STRUCTURE
├── [directory structure]
└── ...

🔧 TECHNOLOGY STACK
• Language: [language] v[version]
• Framework: [framework] v[version]
• Key Dependencies:
  - [dep1]: [purpose]
  - [dep2]: [purpose]
• Testing: [test framework]
• Build: [build tool]

📐 ARCHITECTURE
• Pattern: [MVC/Clean/Layered/Microservices/etc]
• Entry Points:
  - [entry1]: [purpose]
  - [entry2]: [purpose]
• Core Modules:
  - [module1]: [responsibility]
  - [module2]: [responsibility]

🎨 CONVENTIONS
• File Naming: [pattern]
• Function Naming: [camelCase/snake_case/etc]
• Class Naming: [PascalCase/etc]
• Import Style: [pattern]

📋 COMMANDS
• Build: [command]
• Test: [command]
• Lint: [command]
• Dev: [command]

⚠️ NOTES
• [any important observations]
• [gotchas or unusual patterns]

╚══════════════════════════════════════════════════════════════╝
```

## Success Criteria
- Project type clearly identified
- Tech stack documented
- Key patterns understood
- Build/test commands known
- Ready to make changes safely
