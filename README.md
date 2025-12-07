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
  <a href="#-memory-system">Memory System</a> •
  <a href="#-task-flows">Task Flows</a> •
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

**Droidpartment** is a team of 18 specialized AI agents for [Factory AI](https://factory.ai) that work together like a real software development department.

```
┌─────────────────────────────────────────────────────────────────┐
│  YOU: "audit this project"                                      │
│                                                                 │
│  DROIDPARTMENT:                                                 │
│    ├── 🛡️  dpt-sec    → Security audit (OWASP, CWE)            │
│    ├── 👨‍💻 dpt-lead   → Code review (SOLID, clean code)        │
│    ├── 🧪 dpt-qa     → Test coverage (pyramid analysis)        │
│    └── 📊 dpt-output → Results + learning stats                │
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

**That's it!** Now just describe your task naturally.

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
| `dpt-dev` | Code implementation |
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

## 🔄 Task Flows

Choose the right flow for your task:

### 🆕 Feature Development
```
memory(START) → product → arch → scrum
      ↓
    dev → data/api/ux
      ↓
qa + lead + sec + review  ←── PARALLEL
      ↓
memory(END) → output
```

### 🐛 Bug Fix
```
memory(START) → research (reproduce)
      ↓
   5 Whys (root cause)
      ↓
  dev (fix) → qa (regression test)
      ↓
memory(END) → output
```

### 🔍 Audit
```
memory(START)
      ↓
sec + lead + qa + review + perf  ←── ALL PARALLEL
      ↓
memory(END) → output
```

### 📈 Improvement
```
memory(START) → perf (BASELINE)
      ↓
dev (change) → perf (MEASURE)
      ↓
memory(END) → output (before/after)
```

---

## 🧠 Memory System

The secret sauce - **Droidpartment learns from every task!**

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

## 📖 How to Call Agents

**Use Task tool (NOT Skill tool!):**

```javascript
Task(
  subagent_type: "dpt-sec",
  description: "Security audit",
  prompt: "Audit security of this project"
)
```

### Parallel Execution (Independent)
```javascript
// These can run at the same time!
Task(subagent_type: "dpt-sec", ...)
Task(subagent_type: "dpt-lead", ...)
Task(subagent_type: "dpt-qa", ...)
```

### Sequential Execution (Dependent)
```javascript
// Must wait for each to complete
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
│  🎯 SIMPLE > COMPLEX                   │
│  👨‍💻 EXPERT > GENERALIST               │
│  ⚡ PARALLEL > SEQUENTIAL (when safe)  │
│  🧠 LEARN FROM EVERY MISTAKE           │
│  📈 GET SMARTER EVERY RUN              │
└────────────────────────────────────────┘
```

---

## 🗺️ Roadmap

- [x] 18 Expert agents
- [x] Memory system with learning
- [x] PDCA task flows
- [x] Parallel execution
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
