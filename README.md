# 🤖 Droidpartment

**Multi-agent orchestration for Factory AI that learns from every run.**

```bash
npx droidpartment install
```

<p>
  <a href="https://www.npmjs.com/package/droidpartment"><img src="https://img.shields.io/npm/v/droidpartment?style=flat-square&logo=npm&color=CB3837" alt="npm"></a>
  <a href="https://www.npmjs.com/package/droidpartment"><img src="https://img.shields.io/npm/dm/droidpartment?style=flat-square&color=blue" alt="downloads"></a>
  <a href="https://github.com/UntaDotMy/Droidpartment"><img src="https://img.shields.io/github/stars/UntaDotMy/Droidpartment?style=flat-square&logo=github" alt="stars"></a>
  <img src="https://img.shields.io/badge/agents-18-green?style=flat-square" alt="18 agents">
  <img src="https://img.shields.io/badge/dependencies-0-success?style=flat-square" alt="zero deps">
</p>

---

## Why Droidpartment?

| Without | With Droidpartment |
|---------|-------------------|
| AI jumps straight to coding | PRD → Architecture → Stories → Code |
| Hope it works | Parallel QA + Security + Code Review |
| Forgets everything | Learns from every session |
| Gets lost in context | Automatic agent handoffs |

---

## ⚡ Quick Start

```bash
# 1. Install
npx droidpartment install

# 2. Enable in Factory AI: /settings → Experimental → Custom Droids ✓

# 3. Describe your task
"Build user auth with JWT"
```

Droidpartment automatically runs the right agents in the right order.

---

## 🌊 How It Works

```
Wave 1 [INIT]     → dpt-memory + dpt-research (parallel)
Wave 2 [PLAN]     → dpt-product → PRD.md
Wave 3 [DESIGN]   → dpt-arch → ARCHITECTURE.md
Wave 4 [STORIES]  → dpt-scrum → STORIES.md
Wave 5 [CODE]     → dpt-dev (parallel tasks)
Wave 6 [AUDIT]    → dpt-qa + dpt-sec + dpt-lead (parallel)
Wave 7 [FINISH]   → dpt-memory(END) + dpt-output
```

---

## 🤖 Meet the Team

**18 specialized agents**, each expert in one domain:

| Category | Agents | Purpose |
|----------|--------|---------|
| **Memory** | `dpt-memory`, `dpt-output` | Learning system + formatted results |
| **Planning** | `dpt-product`, `dpt-research`, `dpt-arch`, `dpt-scrum` | PRD, research, architecture, stories |
| **Code** | `dpt-dev`, `dpt-data`, `dpt-api`, `dpt-ux` | Implementation specialists |
| **Quality** | `dpt-qa`, `dpt-sec`, `dpt-lead`, `dpt-review`, `dpt-perf` | Testing, security, review |
| **Support** | `dpt-ops`, `dpt-docs`, `dpt-grammar` | DevOps, docs, text |

---

## 🧠 Learning Memory

Droidpartment remembers across sessions:

```
~/.factory/memory/
├── lessons.yaml    ← What worked
├── patterns.yaml   ← Reusable solutions
├── mistakes.yaml   ← What to avoid
└── projects/       ← Per-project knowledge
```

Every session ends with:
```
MEMORY: Lessons: 15 (+2) | Mistakes Prevented: 12 | Learning: 📈 Improving
```

---

## 🪝 Auto Hooks

6 hooks run automatically—zero config:

| Hook | When | What |
|------|------|------|
| `SessionStart` | Session begins | Init cache + memory |
| `UserPromptSubmit` | User sends prompt | Classify task, build workflow |
| `PreToolUse` | Before tool runs | Validate paths, inject context |
| `PostToolUse` | After tool runs | Track progress |
| `SubagentStop` | Agent completes | Handoff context, track waves |
| `SessionEnd` | Session ends | Save stats, cleanup |

**Result:** 70-100% token savings, automatic context passing.

---

## 📋 Commands

```bash
npx droidpartment install     # Install
npx droidpartment update      # Update
npx droidpartment status      # Check status
npx droidpartment uninstall   # Remove
```

| Flag | Description |
|------|-------------|
| `-y` | Auto-confirm |
| `--project` | Install to ./.factory (project-level) |
| `--purge` | Delete memory on uninstall |

---

## 🔄 Example Flows

**Bug Fix:**
```
dpt-memory(START) → dpt-dev → dpt-qa → dpt-memory(END) → dpt-output
```

**Feature:**
```
dpt-memory → dpt-product → dpt-arch → dpt-scrum → dpt-dev → [dpt-qa + dpt-sec + dpt-lead] → dpt-memory → dpt-output
```

**Audit:**
```
dpt-memory → [dpt-sec + dpt-lead + dpt-qa + dpt-perf] → dpt-memory → dpt-output
```

---

## ✨ Key Features

- **Wave Execution** — Parallel [P] and Sequential [S] task grouping
- **Document Artifacts** — Auto-generates PRD.md, ARCHITECTURE.md, STORIES.md
- **Learning Memory** — Captures lessons, patterns, mistakes across sessions
- **Feedback Loops** — Auto-revision when issues found
- **Zero Dependencies** — Pure Python 3.6+ stdlib

---

## �️ Requirements

- **Factory AI** with Custom Droids enabled
- **Python 3.6+** (for hooks)
- **Node.js** (for install)

---

## 📚 More Info

- [CHANGELOG.md](CHANGELOG.md) — Version history
- [templates/AGENTS.md](templates/AGENTS.md) — Detailed agent docs
- [templates/droids/](templates/droids/) — Agent markdown files

---

## 🤝 Contributing

PRs welcome! Fork → branch → commit → PR.

---

## 📄 License

MIT © 2025 [Nasri](https://github.com/UntaDotMy)

---

<p align="center">
  <strong>Made with 🤖 for the Factory AI community</strong><br>
  <sub>If this helps you, give it a ⭐</sub>
</p>
