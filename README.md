<p align="center">
  <pre>
  ____  ____   ___  ___ ____  ____   _    ____ _____ __  __ _____ _   _ _____ 
 |  _ \|  _ \ / _ \|_ _|  _ \|  _ \ / \  |  _ \_   _|  \/  | ____| \ | |_   _|
 | | | | |_) | | | || || | | | |_) / _ \ | |_) || | | |\/| |  _| |  \| | | |  
 | |_| |  _ <| |_| || || |_| |  __/ ___ \|  _ < | | | |  | | |___| |\  | | |  
 |____/|_| \_\\___/|___|____/|_| /_/   \_\_| \_\|_| |_|  |_|_____|_| \_| |_|  
  </pre>
</p>

<h3 align="center">🚀 Multi-Agent Orchestration for Factory AI That Learns From Every Run</h3>

<p align="center">
  <strong>18 specialized agents • Wave execution • Automatic memory • Zero dependencies</strong>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-why-droidpartment">Why Droidpartment</a> •
  <a href="#-the-experts">The Experts</a> •
  <a href="#-how-it-works">How It Works</a> •
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
  <img src="https://img.shields.io/badge/skill-1-blue?style=flat-square" alt="Skill">
  <img src="https://img.shields.io/badge/hooks-6-orange?style=flat-square" alt="Hooks">
  <img src="https://img.shields.io/badge/dependencies-0-success?style=flat-square" alt="Dependencies">
</p>

---

## 🎯 Why Droidpartment?

Unlike generic AI coding assistants, Droidpartment provides **structured, battle-tested workflows** powered by specialized agents who understand software development. Each agent has deep domain expertise—from architecture to security to testing—working together seamlessly.

| Problem | Without Droidpartment | With Droidpartment |
|---------|----------------------|-------------------|
| **Task Planning** | AI jumps straight to coding | Automatic PRD → Architecture → Stories breakdown |
| **Quality** | Hope it works | Parallel audits: Security + QA + Code Review |
| **Memory** | Forgets everything | Learns from every session, remembers mistakes |
| **Workflow** | Chaotic, unpredictable | Wave execution with [P]/[S] markers |
| **Context** | Gets lost in long sessions | Automatic handoffs between agents |

### ✨ Key Benefits

- **Wave Execution** - Tasks grouped into waves for optimal parallel/sequential execution
- **Document Artifacts** - Automatic PRD.md → ARCHITECTURE.md → STORIES.md flow
- **Learning Memory** - Captures lessons, patterns, and mistakes across sessions
- **Zero Config** - Just install and describe your task
- **18 Specialists** - Each agent has deep expertise in one domain

---

## 🚀 Quick Start

### Get Started in 3 Steps

```bash
# 1. Install
npx droidpartment install

# 2. Enable in Factory AI
#    /settings → Experimental → Custom Droids ✓

# 3. Just describe your task!
#    "Build a user authentication system with JWT"
```

That's it. Droidpartment automatically:
- Detects task complexity
- Creates PRD and architecture
- Breaks down into stories
- Implements with parallel audits
- Captures lessons learned

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    WAVE EXECUTION FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Wave 1 [INIT]                                              │
│  ├─ [P] dpt-memory(START)                                   │
│  └─ [P] dpt-research                                        │
│         ↓                                                   │
│  Wave 2 [PLAN]                                              │
│  └─ [S] dpt-product → PRD.md                                │
│         ↓                                                   │
│  Wave 3 [DESIGN]                                            │
│  └─ [S] dpt-arch → ARCHITECTURE.md                          │
│         ↓                                                   │
│  Wave 4 [BREAKDOWN]                                         │
│  └─ [S] dpt-scrum → STORIES.md                              │
│         ↓                                                   │
│  Wave 5 [IMPLEMENT]                                         │
│  ├─ [P] dpt-dev (component 1)                               │
│  └─ [P] dpt-dev (component 2)                               │
│         ↓                                                   │
│  Wave 6 [AUDIT]                                             │
│  ├─ [P] dpt-qa (testing)                                    │
│  ├─ [P] dpt-sec (security)                                  │
│  └─ [P] dpt-lead (code review)                              │
│         ↓                                                   │
│  Wave 7 [FINALIZE]                                          │
│  ├─ [S] dpt-memory(END)                                     │
│  └─ [S] dpt-output                                          │
│                                                             │
│  [P] = Parallel (run simultaneously)                        │
│  [S] = Sequential (wait for previous)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🆚 How Droidpartment Compares

| Feature | Droidpartment | Generic AI | Other Frameworks |
|---------|---------------|------------|------------------|
| **Specialized Agents** | 18 experts | 1 generalist | Varies |
| **Learning Memory** | ✅ Automatic | ❌ None | ⚠️ Manual |
| **Wave Execution** | ✅ Built-in | ❌ No | ⚠️ Some |
| **Document Artifacts** | ✅ PRD/Arch/Stories | ❌ No | ⚠️ Some |
| **Parallel Audits** | ✅ QA+Sec+Review | ❌ No | ⚠️ Manual |
| **Feedback Loops** | ✅ Auto-revision | ❌ No | ⚠️ Manual |
| **Dependencies** | 0 | Varies | Many |
| **Platform** | Factory AI | Any | Varies |

---

## 🐍 Python Backend Infrastructure

**v3.2.0 introduces Python-powered efficiency to all agents**

Droidpartment includes Python modules that eliminate duplicate work:

- **context_index.py** - Project structure caching and file targeting
- **shared_context.py** - Agent output storage and parallel handoffs
- **workflow_state.py** - Wave execution and topology management

### Zero External Dependencies ✓

These Python modules have **no external dependencies** - they work with Python 3.6+.

### How They Work Together

```
Agent 1 → cache_manager → Gets environment without re-discovery
     ↓
   memory_system → Stores results in session
     ↓
   handoff_protocol → Prepares optimized handoff
     ↓
Agent 2 → memory_system → Retrieves Agent 1's results
     ↓
   cache_manager → Uses same cached environment
     ↓
   Continues workflow
```

**Result:** Each task eliminates redundant discovery work and reduces token usage by 20-40%.

---

## 🪝 Automatic Factory Hooks

**v3.2.0 introduces automatic Factory hooks** that trigger at key lifecycle points:

### Zero Configuration Required
After `npm install droidpartment`, hooks register automatically. No manual setup needed.

### Four Automatic Hooks

| Hook | Triggers | What It Does |
|------|----------|-------------|
| **SessionStart** | Session begins | Loads cache + initializes memory ONCE (shared by all 18 agents) |
| **SubagentStop** | Agent completes | Transfers context automatically to next agent |
| **PostToolUse** | After each tool | Tracks progress and updates memory in real-time |
| **SessionEnd** | Session ends | Saves statistics + archives learning + cleanup |

### Benefits

**Before Hooks:**
- 18 agents each discover environment independently (180+ seconds wasted)
- Manual memory management required (dpt-memory END calls)
- No automatic progress tracking
- 1,080-1,440 tokens wasted per session on duplicate discovery

**After Hooks (v3.2.0):**
- Environment discovered ONCE, shared by all 18 agents (10 seconds total)
- Memory management 100% automatic
- Real-time progress tracking
- 1,080-1,440 tokens saved per session (70-100% efficiency gain)

### How It Works

```
USER REQUEST
    ↓
[SessionStart Hook] ← Automatic
    ├─ Load cache (once)
    └─ Init memory
    
dpt-memory → dpt-dev → dpt-qa ← All use shared cache
    ↓              ↓
[SubagentStop]  [PostToolUse] ← Automatic
    
[SessionEnd Hook] ← Automatic
    └─ Save + cleanup

Result: Zero manual intervention, maximum efficiency
```

### Hooks Location

After installation, hooks are located at:
- Personal: `~/.factory/memory/hooks/`
- Project: `./.factory/memory/hooks/`

Registered automatically in `~/.factory/settings.json`

### Troubleshooting

If hooks don't execute:
- Verify Python 3 installed: `python3 --version`
- Check hook registration: `cat ~/.factory/settings.json | grep hooks`
- Re-run installer: `npx droidpartment --update`

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
- 🪝 **Factory Hooks** - Automatic memory management at lifecycle points

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

**That's it!** Hooks register automatically - memory management, context sharing, and progress tracking work out-of-the-box.

---

## ⚠️ Mandatory Workflow (STRICT ENFORCEMENT)

**The main droid MUST use custom droids. It is FORBIDDEN from coding directly.**

### v3.2.0: Strict Enforcement Rules

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

### Self-Verification (v3.2.0)

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

### Main Commands

| Command | Description |
|---------|-------------|
| `npx droidpartment` | Interactive install/update |
| `npx droidpartment install` | Install to ~/.factory |
| `npx droidpartment update` | Update to latest version |
| `npx droidpartment reinstall` | Fresh install (uninstall + install) |
| `npx droidpartment status` | Check installation status |
| `npx droidpartment memory` | Manage/clean memory files |
| `npx droidpartment uninstall` | Remove completely |

### Options

| Option | Description |
|--------|-------------|
| `-y, --yes` | Auto-confirm all prompts |
| `-q, --quiet` | Minimal output |
| `-v, --verbose` | Detailed output |
| `--project` | Install to ./.factory (project-level) |
| `--force` | Force operation |
| `--dry-run` | Preview changes |
| `--purge` | Delete memory on uninstall |
| `--help` | Show help |
| `--version` | Show version |

### Examples

```bash
npx droidpartment install -y         # Quick install
npx droidpartment update             # Update to latest
npx droidpartment status             # Check status
npx droidpartment install --dry-run  # Preview install
npx droidpartment uninstall --purge  # Remove + delete memory
```

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
- [x] **v3.2.0: Strict enforcement with FORBIDDEN actions + nested Task guard**
- [ ] Web dashboard for memory visualization
- [ ] Cross-project pattern sharing
- [ ] Team memory sync

---

## 📚 Learning Resources

Start here to understand how to use Droidpartment:

### Quick References
- **[Agent Efficiency Protocol](templates/droids/)** - How all 18 agents use Python infrastructure
- **[Memory System Guide](README.md#-memory-system)** - Understand lessons and patterns
- **[Workflow Examples](README.md#-example-flows)** - See real task flows

### Agent Templates
Each agent has a dedicated markdown file explaining:
- How to call the agent
- What tools it uses
- How it integrates with the plan system
- Python module usage for efficiency

**18 Agent Templates:**
```
Memory & Output: dpt-memory, dpt-output
Planning: dpt-product, dpt-research, dpt-arch, dpt-scrum
Implementation: dpt-dev, dpt-data, dpt-api, dpt-ux
Quality: dpt-sec, dpt-lead, dpt-qa, dpt-review, dpt-perf
Support: dpt-ops, dpt-docs, dpt-grammar
```

All templates support:
- ✅ Plan system integration
- ✅ Python infrastructure (cache_manager, memory_system, handoff_protocol)
- ✅ PDCA hooks (Plan-Do-Check-Act)
- ✅ Cross-agent communication

### Python Infrastructure

**Location:** `~/.factory/droids/python/`

**Three Core Modules:**

1. **cache_manager.py** - Environment caching
   ```python
   from cache_manager import get_agent_context, get_environment_info
   context = get_agent_context("dpt-dev")
   env = get_environment_info()
   ```

2. **memory_system.py** - Cross-agent results storage
   ```python
   from memory_system import store_in_session, get_from_session
   store_in_session("dpt-dev", "results", {"status": "done"})
   ```

3. **handoff_protocol.py** - Agent coordination
   ```python
   from handoff_protocol import prepare_handoff_to
   handoff = prepare_handoff_to("dpt-dev", "dpt-qa", results)
   ```

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
