# Memory Skill - Human-Like Learning System

## Purpose

Provides persistent, project-specific memory that learns from mistakes, gains knowledge automatically, and makes all agents smarter over time.

## Memory Architecture (Based on Human Cognition)

```
.factory/memory/
├── episodic.yaml      # Specific events: fixes, errors, solutions
├── semantic.yaml      # General knowledge: patterns, best practices
├── lessons.yaml       # Lessons learned from mistakes
└── index.yaml         # Quick lookup tags
```

## Memory Types

### 1. Episodic Memory (Events)
What happened, when, where, how it was fixed.
```yaml
- id: ep_20241206_001
  timestamp: 2024-12-06T14:30:00
  type: fix
  context:
    file: src/db/connection.ts
    error: "Connection timeout after 30s"
  problem: Database connections exhausting pool
  solution: Increased pool size from 5 to 20, added connection cleanup
  outcome: success
  tags: [database, timeout, connection-pool]
```

### 2. Semantic Memory (Knowledge)
General facts and patterns extracted from experience.
```yaml
database:
  connection-pool:
    - "Default pool sizes (5-10) are often too small for production"
    - "Always implement connection cleanup/release"
    - "Monitor active connections to detect leaks"
  timeouts:
    - "30s timeout usually indicates pool exhaustion, not slow queries"
    - "Check pool size before optimizing queries"
```

### 3. Lessons Learned (Error Corrections)
When user confirms "it's working now" - capture the lesson.
```yaml
- id: lesson_001
  trigger: "User confirmed fix works"
  mistake: "Assumed timeout was query performance issue"
  correction: "Actually was connection pool exhaustion"
  lesson: "Check connection pool metrics before optimizing queries"
  applies_to: [database, timeout, performance]
```

## Memory Operations

### CAPTURE (After Success)
When user confirms something works:
1. Identify what was fixed/learned
2. Summarize in 1-3 sentences (no verbose logs)
3. Extract tags for retrieval
4. Store in appropriate memory type
5. Update index

### RETRIEVE (Before Decisions)
Before making changes:
1. Identify current context (file type, error type, domain)
2. Search index for relevant tags
3. Load matching memories
4. Apply knowledge to current situation

### CONSOLIDATE (Periodic)
When memories accumulate:
1. Find similar episodic memories
2. Extract common patterns
3. Create semantic knowledge entry
4. Archive old episodic entries

### FORGET (Cleanup)
Remove outdated memories:
1. Contradicted by newer knowledge
2. No longer relevant to project
3. Superseded by consolidated knowledge

## Trigger Patterns

### Auto-Capture Triggers
| User Says | Action |
|-----------|--------|
| "it works", "fixed", "working now" | Capture as lesson learned |
| "that's correct", "yes", "perfect" | Reinforce current approach |
| "no", "wrong", "not that" | Record what NOT to do |
| After successful test run | Capture working patterns |
| After successful deploy | Capture deployment knowledge |

### Auto-Retrieve Triggers
| Context | Action |
|---------|--------|
| Similar error message | Search episodic for past fixes |
| Same file type | Load relevant patterns |
| Same domain (db, api, ui) | Load domain knowledge |
| Before any fix attempt | Check if seen before |

## Memory Format (YAML)

Using YAML because research shows:
- Best LLM understanding of nested data
- Human-readable for debugging
- Efficient token usage
- Easy to parse and update

## Summary Guidelines

### DO:
- Summarize in 1-3 sentences
- Focus on the lesson, not the details
- Include actionable knowledge
- Tag for easy retrieval

### DON'T:
- Store full stack traces
- Store entire file contents
- Store verbose logs
- Duplicate existing knowledge

## Example Memory Flow

```
1. User: "There's a timeout error in database"
   
2. RETRIEVE: Search memories for [database, timeout]
   → Found: "30s timeout usually indicates pool exhaustion"
   → Agent checks pool size first (learned behavior)

3. Agent: "I found pool size is 5, increasing to 20"
   
4. User: "It's working now!"

5. CAPTURE:
   - Episodic: Fixed timeout in src/db by increasing pool from 5→20
   - Lesson: Small pool size causes timeout under load
   - Tags: [database, timeout, connection-pool, fix]

6. Next time similar error → Agent already knows to check pool size
```

## Integration Protocol

All agents include at session start:
```
MEMORY PROTOCOL:
1. Before decisions → Retrieve relevant memories
2. After user confirms success → Capture lesson
3. Apply learned patterns to current work
```

## Per-Project Isolation

Memories stored in `.factory/memory/` within each project.
No cross-project contamination.
Each project builds its own knowledge base.
