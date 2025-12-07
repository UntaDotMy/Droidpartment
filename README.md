<p align="center">
  <pre>
  ____  ____   ___  ___ ____  ____   _    ____ _____ __  __ _____ _   _ _____ 
 |  _ \|  _ \ / _ \|_ _|  _ \|  _ \ / \  |  _ \_   _|  \/  | ____| \ | |_   _|
 | | | | |_) | | | || || | | | |_) / _ \ | |_) || | | |\/| |  _| |  \| | | |  
 | |_| |  _ <| |_| || || |_| |  __/ ___ \|  _ < | | | |  | | |___| |\  | | |  
 |____/|_| \_\\___/|___|____/|_| /_/   \_\_| \_\|_| |_|  |_|_____|_| \_| |_|  
  </pre>
</p>

<p align="center">
  <strong>🤖 18 Expert AI Agents That Learn & Get Smarter Every Run</strong>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-the-experts">The Experts</a> •
  <a href="#-mandatory-workflow">Workflow</a> •
  <a href="#-memory-system">Memory</a> •
  <a href="#-commands">Commands</a>
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/droidpartment"><img src="https://img.shields.io/npm/v/droidpartment?style=for-the-badge&logo=npm&logoColor=white&label=npm&color=CB3837" alt="npm version"></a>
  <a href="https://www.npmjs.com/package/droidpartment"><img src="https://img.shields.io/npm/dm/droidpartment?style=for-the-badge&logo=npm&logoColor=white&color=CB3837" alt="npm downloads"></a>
  <a href="https://github.com/UntaDotMy/Droidpartment"><img src="https://img.shields.io/github/stars/UntaDotMy/Droidpartment?style=for-the-badge&logo=github&color=181717" alt="GitHub stars"></a>
  <a href="https://github.com/UntaDotMy/Droidpartment/blob/main/LICENSE"><img src="https://img.shields.io/npm/l/droidpartment?style=for-the-badge&color=blue" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/agents-18-green?style=flat-square" alt="Agents">
  <img src="https://img.shields.io/badge/platform-Factory_AI-purple?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/node-%3E%3D16.0.0-brightgreen?style=flat-square&logo=node.js" alt="Node">
  <img src="https://img.shields.io/badge/dependencies-0-success?style=flat-square" alt="Dependencies">
</p>

---

## 🧠 What Is This?

**Droidpartment** is a team of 18 specialized AI agents for [Factory AI](https://factory.ai) that work together like a real software development department. The main droid **delegates** to experts instead of doing everything itself.

```
┌─────────────────────────────────────────────────────────────────┐
│  YOU: "fix the bug in auth"                                     │
│                                                                 │
│  MAIN DROID: (follows mandatory workflow)                       │
│    1. dpt-memory  → "START - bug fix for auth"                 │
│    2. dpt-dev     → Implements the fix                         │
│    3. dpt-qa      → Tests the fix                              │
│    4. dpt-memory  → "END - captures lessons"                   │
│    5. dpt-output  → Formats results with stats                 │
│                                                                 │
│  MEMORY: Lessons: 12 (+3) | Mistakes Prevented: 5               │
└─────────────────────────────────────────────────────────────────┘
```

### ✨ Key Features

- 🎯 **Expert Specialists** - Each agent masters one domain
- 🧠 **Memory System** - Learns from every task, prevents repeated mistakes
- ⚡ **Parallel Execution** - Run independent audits simultaneously
- 📈 **Learning Curve** - Gets smarter with every session
- 🔄 **PDCA Cycle** - Plan-Do-Check-Act methodology built-in
- ✅ **Strict Enforcement** - Main droid FORBIDDEN from coding directly

---

## 🚀 Quick Start

```bash
# Install globally
npm install -g droidpartment
droidpartment

# Or one-time with npx
npx droidpartment
```

**After install:**
1. Open Factory AI settings: `/settings`
2. Go to **Experimental** → Enable **Custom Droids**
3. Restart CLI

**That's it!** The main droid will now follow the mandatory workflow.

---

## ⚠️ Mandatory Workflow (STRICT ENFORCEMENT)

**The main droid MUST use custom droids. It is FORBIDDEN from coding directly.**

### v3.0.7: Strict Enforcement Rules

```
FORBIDDEN ACTIONS:
❌ NEVER use Edit/Create for code without calling dpt-dev FIRST
❌ NEVER use TodoWrite without calling dpt-scrum FIRST (3+ steps)
❌ NEVER start ANY task without dpt-memory START
❌ NEVER complete ANY task without dpt-memory END
❌ NEVER respond without dpt-output (multi-step tasks)
```

### Task Classification

| User Request Contains | Task Type | Required Flow |
|----------------------|-----------|---------------|
| "audit", "review", "check" | AUDIT | memory → sec+lead+qa+perf → memory → output |
| "fix", "bug", "error" | BUG_FIX | memory → dev → qa → memory → output |
| "add", "create", "build" | FEATURE | memory → product → arch → scrum → dev → qa → sec → memory → output |
| "update", "change" | IMPLEMENTATION | memory → scrum → dev → lead → qa → memory → output |

### The Rules

```
RULE 1: ALWAYS start with dpt-memory
RULE 2: Classify task → follow REQUIRED flow
RULE 3: NEVER code directly → use dpt-dev
RULE 4: NEVER skip steps
RULE 5: Memory END → then Output (sequential)
```

### Self-Verification (v3.0.7)

Before every action, main droid must ask:
```
"CHECKPOINT: Am I following the droid workflow?"
"CHECKPOINT: Did dpt-dev provide this code, or am I writing it myself?"
```

---

## 👥 The Experts

<table>
<tr>
<td width="50%">

### 🧠 Memory & Output
| Agent | Role |
|-------|------|
| `dpt-memory` | Learning system (START/END) |
| `dpt-output` | Format results + stats |

### 📋 Planning
| Agent | Role |
|-------|------|
| `dpt-product` | Requirements, user stories |
| `dpt-research` | Best practices (official docs) |
| `dpt-arch` | Architecture, ADRs |
| `dpt-scrum` | Task breakdown |

### 💻 Implementation
| Agent | Role |
|-------|------|
| `dpt-dev` | **ALL code implementation** |
| `dpt-data` | Database, queries |
| `dpt-api` | API design (REST) |
| `dpt-ux` | UI/UX, accessibility |

</td>
<td width="50%">

### ✅ Quality (Can Run Parallel!)
| Agent | Role |
|-------|------|
| `dpt-sec` | Security (OWASP, CWE) |
| `dpt-lead` | Code review (SOLID) |
| `dpt-qa` | Testing (pyramid) |
| `dpt-review` | Simplicity (YAGNI) |
| `dpt-perf` | Performance |

### 🔧 Support
| Agent | Role |
|-------|------|
| `dpt-ops` | DevOps, CI/CD |
| `dpt-docs` | Documentation |
| `dpt-grammar` | Text clarity |

</td>
</tr>
</table>

---

## 🔄 Example Flows

### Bug Fix Flow
```
1. dpt-memory  → "START - bug fix for [issue]"     WAIT
2. dpt-dev     → "Fix the bug in [file]"           WAIT
3. dpt-qa      → "Test the fix"                    WAIT
4. dpt-memory  → "END - bug fixed, lessons..."     WAIT
5. dpt-output  → "Format results"                  LAST
```

### Feature Flow
```
1. dpt-memory  → "START - new feature [name]"      WAIT
2. dpt-product → "Define requirements"             WAIT
3. dpt-arch    → "Design architecture"             WAIT
4. dpt-scrum   → "Break down tasks"                WAIT
5. dpt-dev     → "Implement feature"               WAIT
6. dpt-qa      → "Test feature"                    PARALLEL
7. dpt-sec     → "Security check"                  PARALLEL
8. dpt-memory  → "END - feature complete"          WAIT
9. dpt-output  → "Format results"                  LAST
```

### Audit Flow
```
1. dpt-memory  → "START - audit [project]"         WAIT
2. dpt-sec     → "Security audit"                  PARALLEL
3. dpt-lead    → "Code review"                     PARALLEL
4. dpt-qa      → "Test coverage"                   PARALLEL
5. dpt-perf    → "Performance check"               PARALLEL
6. dpt-memory  → "END - audit complete"            WAIT
7. dpt-output  → "Format results"                  LAST
```

---

## 🧠 Memory System

**Droidpartment learns from every task!**

```
~/.factory/memory/
├── 📚 lessons.yaml     ← What worked
├── 🎯 patterns.yaml    ← Reusable solutions
├── ⚠️  mistakes.yaml    ← What to avoid (+prevention)
└── 📁 projects/
    └── {project}/      ← Project-specific knowledge
```

### Learning Metrics

| Status | Meaning |
|--------|---------|
| 📈 **Improving** | Prevented > New mistakes |
| ➡️ **Stable** | Prevented = New mistakes |
| ⚠️ **Needs Attention** | Prevented < New mistakes |

### Every Task Ends With:
```
MEMORY STATUS:
Project: MyProject
Lessons: 15 (+2)
Mistakes: 8 (+1)
Prevented: 12
Learning: 📈 Improving
```

---

## 📖 How Agents Are Called

**Use Task tool (NOT Skill tool!):**

```javascript
Task(
  subagent_type: "dpt-dev",
  description: "Implement feature",
  prompt: "Implement [requirement] in [file]. Follow existing patterns."
)
```

### Parallel (Independent)
```javascript
// These can run at the same time!
Task(subagent_type: "dpt-sec", ...)
Task(subagent_type: "dpt-lead", ...)
Task(subagent_type: "dpt-qa", ...)
```

### Sequential (Must Wait)
```javascript
Task(subagent_type: "dpt-memory", prompt: "START...")  // WAIT
Task(subagent_type: "dpt-dev", ...)                     // WAIT
Task(subagent_type: "dpt-memory", prompt: "END...")    // WAIT
Task(subagent_type: "dpt-output", ...)                  // LAST
```

---

## 🛠️ Commands

| Command | Description |
|---------|-------------|
| `npx droidpartment` | Install or update |
| `npx droidpartment --memory` | Manage/clean memory |
| `npx droidpartment --uninstall` | Remove completely |
| `npx droidpartment --help` | Show help |
| `npx droidpartment --version` | Show version |

---

## 📍 Install Locations

| Location | Path | Best For |
|----------|------|----------|
| **Personal** | `~/.factory/` | Works in ALL projects ✨ |
| **Project** | `./.factory/` | Team sharing via git |

---

## 💡 Philosophy

```
┌────────────────────────────────────────┐
│  🎯 DELEGATE > DO IT YOURSELF          │
│  👨‍💻 EXPERT > GENERALIST               │
│  ⚡ PARALLEL > SEQUENTIAL (when safe)  │
│  🧠 LEARN FROM EVERY MISTAKE           │
│  📈 GET SMARTER EVERY RUN              │
│  ✅ FOLLOW THE WORKFLOW                │
└────────────────────────────────────────┘
```

---

## 🗺️ Roadmap

- [x] 18 Expert agents
- [x] Memory system with learning
- [x] PDCA task flows
- [x] Parallel execution
- [x] Mandatory workflow enforcement
- [x] **v3.0.7: Strict enforcement with FORBIDDEN actions**
- [ ] Web dashboard for memory visualization
- [ ] Cross-project pattern sharing
- [ ] Team memory sync

---

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

MIT © 2025 [Nasri](https://github.com/UntaDotMy)

---

<p align="center">
  <a href="https://github.com/UntaDotMy/Droidpartment">
    <img src="https://img.shields.io/badge/GitHub-UntaDotMy%2FDroidpartment-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
  <a href="https://www.npmjs.com/package/droidpartment">
    <img src="https://img.shields.io/badge/npm-droidpartment-CB3837?style=for-the-badge&logo=npm" alt="npm">
  </a>
</p>

<p align="center">
  <strong>Made with 🤖 for the Factory AI community</strong>
</p>

<p align="center">
  <sub>If this helps you, give it a ⭐!</sub>
</p>
