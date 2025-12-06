---
name: droidpartment
description: Use for ANY software development task - coding, debugging, testing, architecture, security, performance, API design, documentation. Delegates to specialized team of 18 AI agents led by dpt-chief.
---

# Droidpartment - Autonomous Software Development

When this skill is active, delegate ALL work to the dpt-chief subagent.

## Instructions

1. **IMMEDIATELY** call Task tool with:
   - subagent_type: "dpt-chief"
   - prompt: Pass the user's full request

2. **DO NOT** attempt the task yourself

3. **dpt-chief will**:
   - Analyze the request
   - Call specialized agents (dpt-dev, dpt-qa, dpt-sec, etc.)
   - Validate output
   - Return production-ready result

## Example

User asks: "Add authentication to my app"

You do:
```
Task tool
  subagent_type: "dpt-chief"
  prompt: "User wants to add authentication to their app. Take ownership and deliver production-ready code."
```

## When to Use

- ANY coding task
- ANY debugging task
- ANY testing task
- ANY architecture question
- ANY security review
- ANY performance optimization
- ANY API design
- ANY documentation request

## Success Criteria

- Task delegated to dpt-chief
- dpt-chief returns completed work
- Output is production-ready
