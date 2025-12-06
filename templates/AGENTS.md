# Droidpartment - Auto Delegation

## CRITICAL RULE

**For EVERY task, ALWAYS use the Task tool to delegate to subagent `dpt-chief` first.**

dpt-chief is the team leader who orchestrates 18 specialized agents.

## How to Delegate

```
Task tool → subagent_type: "dpt-chief" → pass user's request
```

## Example

User: "Add login feature"
You: Call Task tool with subagent_type="dpt-chief", prompt="User wants to add login feature. Take ownership and deliver."

## Available Subagents (called by dpt-chief)

- dpt-chief - Team leader (ALWAYS call this first)
- dpt-memory - Learning system
- dpt-research - Official docs research
- dpt-dev - Implementation
- dpt-arch - Architecture
- dpt-qa - Testing
- dpt-sec - Security
- dpt-ops - DevOps
- dpt-lead - Code review
- dpt-docs - Documentation
- dpt-data - Database
- dpt-perf - Performance
- dpt-ux - UI/UX
- dpt-api - API design
- dpt-review - Anti-over-engineering
- dpt-output - Output formatting

## Rules

1. ALWAYS delegate to dpt-chief first
2. Do NOT handle tasks yourself when dpt-chief exists
3. dpt-chief will call other agents as needed
4. Simple > Complex
