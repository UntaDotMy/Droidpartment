---
name: droidpartment-research
description: Research best practices from official sources before implementation.
---

# Research Workflow

Use this skill when you need to research best practices before implementing.

## When to Use

- New technology decisions
- "What's the best way to..." questions
- Architecture decisions
- Library/framework selection
- Implementation patterns

## Workflow

```
1. Task(dpt-memory, "START: research [topic]")
2. Task(dpt-research, "find best practices for [topic]")
3. Task(dpt-arch, "analyze options and trade-offs")
4. Task(dpt-review, "check for over-engineering risks")
5. Task(dpt-memory, "END: decision made, rationale captured")
6. Task(dpt-output, "summarize findings")
```

## Research Priority

1. **Official documentation** - Framework/library docs
2. **RFCs/Standards** - Authoritative specs (RFC, W3C)
3. **Reputable sources** - Known experts, official blogs
4. **Community** - Stack Overflow (verify first)

## Example

```javascript
// User: "What's the best auth strategy for our API?"
Task(dpt-memory, "START: research API authentication")
Task(dpt-research, "best practices for API auth: JWT, OAuth2, sessions")
Task(dpt-arch, "compare options for our scale and requirements")
Task(dpt-review, "check if proposed solution is appropriate complexity")
Task(dpt-memory, "END: JWT selected, rationale documented")
Task(dpt-output, "summarize auth strategy decision")
```

## Output Format

```
Summary: Research complete - [decision made]

Findings:
- Option 1: [name] - [pros/cons]
- Option 2: [name] - [pros/cons]
- Recommended: [option] because [rationale]

Sources:
- [Official doc]: [URL]
- [RFC/Standard]: [URL]
```
