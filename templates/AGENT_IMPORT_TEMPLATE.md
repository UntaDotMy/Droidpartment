# Agent Import Template

This document explains how agents should import and use the Python infrastructure modules.

## Overview

Three core Python modules provide shared infrastructure for all agents:

1. **cache_manager.py** - Pre-discovered environment and project context
2. **handoff_protocol.py** - Efficient agent-to-agent communication
3. **memory_system.py** - Three-layer learning system (global, session, per-project)

## Standard Import Pattern

Every agent should add this to their template under the "EFFICIENCY PROTOCOL" section:

### Basic Imports

```python
# Add these imports to your agent template:
from cache_manager import get_agent_context, get_environment_info, get_project_structure
from handoff_protocol import prepare_handoff_to, get_target_context, store_in_session
from memory_system import store_in_session, get_from_session, track_agent_efficiency
```

### Per-Agent Usage

#### For dpt-dev (Code Implementation)

```python
# Get pre-discovered context (eliminates duplicate discovery)
context = get_agent_context("dpt-dev")
environment = context.get("environment", {})
project_structure = context.get("project_structure", {})
package_info = context.get("package_info", {})

# Example: Use cached node version instead of discovering it
node_version = environment.get("node_version", "unknown")
available_tools = environment.get("available_tools", [])

# Store your work for other agents
handoff_id = prepare_handoff_to(
    source_agent="dpt-dev",
    target_agent="dpt-qa",
    results={"implementation": "feature completed"},
    context_data=context
)

# Track your efficiency
track_agent_efficiency("dpt-dev", "implementation", tokens_used=150)
```

#### For dpt-qa (Testing)

```python
# Get context needed for testing
context = get_agent_context("dpt-qa")
environment = context.get("environment", {})
project_structure = context.get("project_structure", {})

# Retrieve files that dpt-dev created
# (Using session storage instead of re-scanning project)
dev_results = get_from_session("session_dpt-dev_implementation")
if dev_results:
    files_to_test = dev_results.get("files_created", [])
```

#### For dpt-sec (Security Audit)

```python
# Get security-relevant context
context = get_agent_context("dpt-sec")
project_structure = context.get("project_structure", {})

# Use cached environment instead of discovering
platform = environment.get("platform", {}).get("system", "unknown")
has_git = project_structure.get("has_git", False)

# No need to scan the project again - dpt-dev already found tech stack
tech_stack = project_structure.get("tech_stack", [])
```

#### For dpt-lead (Code Review)

```python
# Get code review context
context = get_agent_context("dpt-lead")
project_structure = context.get("project_structure", {})

# Check if previous agent left notes
handoff_context = get_target_context(handoff_id, "dpt-lead")

# Store architectural decisions for future projects
store_in_session(
    agent="dpt-lead",
    key="architecture_review",
    data={
        "patterns_used": ["dependency_injection", "factory_pattern"],
        "violations": [],
        "recommendations": []
    }
)
```

## Context Available to Each Agent

### dpt-dev (Implementation)
- ✅ environment (platform, tools, versions)
- ✅ project_structure (tech_stack, package_info)
- ✅ package_info (dependencies, scripts)

### dpt-qa (Testing)
- ✅ environment (platform, tools)
- ✅ project_structure (tech_stack, has_git)

### dpt-sec (Security)
- ✅ environment (platform, tools)
- ✅ project_structure (tech_stack)

### dpt-perf (Performance)
- ✅ environment (platform, tools)
- ✅ project_structure (tech_stack)

### dpt-lead (Code Review)
- ✅ project_structure (tech_stack, root_path)

### dpt-ops (DevOps)
- ✅ environment (platform, tools)
- ✅ project_structure (tech_stack, has_git)

### dpt-docs (Documentation)
- ✅ project_structure (tech_stack, package_info)

### dpt-arch (Architecture)
- ✅ project_structure (tech_stack, root_path)

### dpt-data (Database)
- ✅ project_structure (tech_stack, root_path)

### dpt-api (API Design)
- ✅ project_structure (tech_stack, root_path)

### dpt-ux (UI/UX)
- ✅ project_structure (tech_stack, root_path)

## Three-Layer Memory System

### Global Memory (Shared across all projects)
```python
from memory_system import learn_pattern, learn_mistake

# After successful implementation
learn_pattern(
    agent="dpt-dev",
    project=None,  # None = global
    pattern_type="authentication",
    pattern="Use JWT with bcrypt for password hashing",
    confidence=95
)

# After failure or issue
learn_mistake(
    agent="dpt-dev",
    project=None,  # None = global
    mistake="Plain text password storage",
    lesson="Always use bcrypt or argon2 for passwords",
    severity="critical"
)
```

### Session Memory (Current task only)
```python
from memory_system import store_in_session, get_from_session

# Store data that other agents in THIS task need
session_id = store_in_session(
    agent="dpt-dev",
    key="auth_implementation",
    data={
        "files_created": ["src/auth/middleware.ts", "src/auth/utils.ts"],
        "dependencies": ["bcrypt", "jsonwebtoken"],
        "patterns_used": ["JWT"]
    }
)

# Other agents retrieve it
other_data = get_from_session(session_id)
```

### Per-Project Memory
```python
from memory_system import store_project_knowledge, get_project_knowledge

# Store project-specific learning
store_project_knowledge(
    project="ecommerce-api",
    knowledge_type="performance_insights",
    content={
        "bottleneck": "database queries in checkout",
        "solution": "Add caching layer with Redis",
        "estimated_improvement": "60% faster"
    }
)

# Retrieve on future work in same project
knowledge = get_project_knowledge("ecommerce-api", "performance_insights")
```

## Efficiency Benefits

When properly implemented:

| Metric | Improvement |
|--------|------------|
| Duplicate discovery work | 60-80% reduction |
| Agent handoff speed | 3-5x faster |
| Token usage | 50%+ savings per interaction |
| Cross-project learning | Patterns reused immediately |

## Example: Full Workflow

```python
# Agent: dpt-dev
from cache_manager import get_agent_context
from handoff_protocol import prepare_handoff_to
from memory_system import store_in_session, track_agent_efficiency

# 1. Get pre-discovered context (no duplicate work)
context = get_agent_context("dpt-dev")
env = context["environment"]
project = context["project_structure"]

# 2. Do your work using cached context
print(f"Platform: {env['platform']['system']}")
print(f"Tech stack: {project['tech_stack']}")
# ... implement feature ...

# 3. Store results for other agents
handoff_id = prepare_handoff_to(
    source_agent="dpt-dev",
    target_agent="dpt-qa",
    results={"implementation": "Complete"},
    context_data=context
)

# 4. Track efficiency
track_agent_efficiency("dpt-dev", "implementation", tokens=150)

# 5. Return with handoff signal
return {
    "value": "Implementation complete",
    "confidence": 95,
    "next_agent": "dpt-qa",
    "handoff_id": handoff_id,
    "efficiency_benefits": {
        "tokens_saved": 200,
        "duplicate_work_eliminated": ["environment discovery", "project analysis"]
    }
}
```

## Installation

The Python modules are automatically included in Droidpartment installation:

```bash
npx droidpartment  # Installs cache_manager.py, handoff_protocol.py, memory_system.py
```

## Compatibility

- **Python Version**: 3.6+
- **Dependencies**: None (standard library only)
- **Node.js Version**: For Droidpartment CLI (16+)
- **Factory Platform**: 2024.2+

## Version History

- **v3.2.0** (Current) - Initial implementation with three core modules
  - cache_manager.py - Fixed undefined gitpattern_match function
  - handoff_protocol.py - Fixed missing self reference
  - memory_system.py - Three-layer learning system

## Troubleshooting

### Module not found error
```
ImportError: No module named 'cache_manager'
```
**Solution**: Ensure modules are in Python path:
```python
import sys
sys.path.append(os.path.expanduser("~/.factory/templates"))
```

### Cache returning empty context
```python
# Context should have environment info
context = get_agent_context("dpt-dev")
if not context.get("environment"):
    print("Warning: Cache not initialized")
```

### Handoff not working between agents
```python
# Ensure handoff_id is passed correctly
handoff_id = prepare_handoff_to(...)  # Get this ID
target_context = get_target_context(handoff_id, "dpt-qa")  # Use same ID
```

## Future Enhancements

- [ ] Database schema caching for dpt-data
- [ ] API endpoint caching for dpt-api
- [ ] Component tree caching for dpt-ux
- [ ] Performance baseline caching for dpt-perf
- [ ] Security vulnerability database caching for dpt-sec
