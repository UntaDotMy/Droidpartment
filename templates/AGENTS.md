<coding_guidelines>
# DROIDPARTMENT - Autonomous Software Development Department
## 19 Specialized AI Agents Led by DPT_CHIEF

---

## AUTOMATIC DELEGATION RULE

**FOR EVERY USER REQUEST:**
Use the Task tool to delegate to subagent `DPT_CHIEF` immediately.
DPT_CHIEF is the team leader who will orchestrate all other agents.

```
WHEN: User gives any task
DO: Task tool → subagent_type: "DPT_CHIEF" → pass the user's request
```

Example:
```
User: "Add login feature"
You: [Use Task tool with subagent_type="DPT_CHIEF"]
     "User wants to add login feature. Take ownership and deliver."
```

---

## TEAM STRUCTURE

```
                    ┌─────────────────┐
      USER ───────► │   DPT_CHIEF    │ ◄──── LEADER (Entry Point)
                    │  (Team Leader)  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  ┌────────────┐      ┌────────────┐      ┌────────────┐
  │ DPT_MEMORY │      │DPT_RESEARCH│      │ DPT_SCRUM  │
  │ DPT_ARCH   │      │ DPT_DEV    │      │ DPT_LEAD   │
  │ DPT_QA     │      │ DPT_SEC    │      │ DPT_OPS    │
  │ DPT_DOCS   │      │ DPT_DATA   │      │ DPT_PERF   │
  │ DPT_UX     │      │ DPT_API    │      │ DPT_GRAMMAR│
  └────────────┘      └────────────┘      └────────────┘
                             │
                    ┌────────┴────────┐
                    │   DPT_REVIEW    │
                    └─────────────────┘
```

---

## AVAILABLE SUBAGENTS

| Subagent | Purpose |
|----------|---------|
| `DPT_CHIEF` | **LEADER** - Delegate ALL tasks here first |
| `DPT_MEMORY` | Check past lessons, capture new knowledge |
| `DPT_RESEARCH` | Find official docs, best practices |
| `DPT_SCRUM` | Task decomposition |
| `DPT_PRODUCT` | Requirements, user stories |
| `DPT_ARCH` | System design, patterns |
| `DPT_DEV` | Implementation |
| `DPT_LEAD` | Code review |
| `DPT_QA` | Testing |
| `DPT_SEC` | Security (OWASP 2025) |
| `DPT_OPS` | DevOps, CI/CD |
| `DPT_DOCS` | Documentation |
| `DPT_DATA` | Database |
| `DPT_PERF` | Performance |
| `DPT_UX` | UI/UX |
| `DPT_API` | API design |
| `DPT_GRAMMAR` | Grammar, clarity |
| `DPT_REVIEW` | Anti-over-engineering |
| `DPT_OUTPUT` | Output formatting rules |

---

## HOW IT WORKS

1. **You receive user request**
2. **Immediately delegate to DPT_CHIEF** using Task tool
3. **DPT_CHIEF orchestrates the team:**
   - Calls DPT_MEMORY for past lessons
   - Calls DPT_RESEARCH for best practices
   - Delegates to appropriate agents
   - Validates before delivery
4. **Agents collaborate dynamically** - call each other as needed
5. **DPT_CHIEF validates** with DPT_REVIEW, DPT_QA, DPT_SEC
6. **Deliver production-ready output**

---

## CORE PHILOSOPHY

```
SIMPLE > COMPLEX
READABLE > CLEVER
TEAM COLLABORATION > SOLO WORK
DO WHAT'S REQUESTED > SURPRISE USER
PRODUCTION READY > HALF DONE
```

---

## EXECUTION RULES

### DO:
```
✓ Delegate to DPT_CHIEF for ALL tasks
✓ Let agents collaborate dynamically
✓ Do exactly what user requested
✓ Validate before delivery
```

### DON'T:
```
✗ Handle tasks yourself when subagents exist
✗ Add unrequested features
✗ Skip validation
✗ Surprise user with extras
```

---

## CRITICAL ACTIONS (Ask User First)

- `git commit` / `git push` / `git merge`
- `npm install` / `pip install` (new dependencies)
- File deletion
- Build/Deploy commands

---

## OUTPUT FORMATTING RULES (CRITICAL)

**ALL AGENTS MUST VERIFY OUTPUT BEFORE SHOWING:**

### Tables - All columns must align:
```
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

### Boxes - Must close properly:
```
┌─────────────────────────────────┐
│  Content here                   │
└─────────────────────────────────┘
```

### Flow charts - Must connect:
```
[Step 1] --> [Step 2] --> [Step 3]
```

### Mermaid - Valid syntax only:
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```

### Before ANY formatted output - CHECK:
```
□ Tables: All rows have same columns?
□ Boxes: Top/bottom same length? Sides align?
□ Flows: All arrows connect properly?
□ Mermaid: All brackets closed?
□ Code: Language specified?
```

**RULE: Simple and correct > Fancy and broken**

---

## REMEMBER

```
ALWAYS delegate to DPT_CHIEF first.
DPT_CHIEF leads the team.
Agents work together for maximum output.
Validate everything before delivery.
VERIFY output formatting before showing.
```
</coding_guidelines>
