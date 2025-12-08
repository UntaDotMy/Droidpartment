#!/usr/bin/env python3
"""
Factory Droid Hook: UserPromptSubmit (Enhanced v2)
Triggers when user submits a prompt.

Features:
- Scale-Adaptive Task Detection (auto-adjust workflow depth)
- Auto-Spec Flow for complex tasks
- Enriches prompt with relevant memory context
- Injects project-specific patterns and lessons
- Adds workflow state for continuity
- Provides mistake prevention reminders

Input: JSON from stdin with prompt
Output: JSON with hookSpecificOutput.additionalContext

Per Factory AI specification:
- stdout is added to context for Droid
- hookSpecificOutput.additionalContext adds string to context
- decision: "block" prevents prompt processing (not used here)
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add memory directory to path for imports
memory_dir = Path(os.path.expanduser('~/.factory/memory'))
sys.path.insert(0, str(memory_dir))


def load_relevant_lessons(prompt: str, max_lessons: int = 3) -> list:
    """Load lessons relevant to the prompt."""
    lessons = []
    
    try:
        lessons_file = memory_dir / 'lessons.yaml'
        if lessons_file.exists():
            content = lessons_file.read_text()
            
            # Simple relevance matching based on keywords
            prompt_lower = prompt.lower()
            keywords = set(prompt_lower.split())
            
            # Parse YAML manually (no deps)
            current_lesson = {}
            for line in content.split('\n'):
                if line.strip().startswith('- id:'):
                    if current_lesson and 'lesson' in current_lesson:
                        lessons.append(current_lesson)
                    current_lesson = {'id': line.split(':', 1)[1].strip()}
                elif ':' in line and current_lesson:
                    key, value = line.strip().split(':', 1)
                    key = key.strip().lstrip('- ')
                    current_lesson[key] = value.strip().strip('"\'')
            
            if current_lesson and 'lesson' in current_lesson:
                lessons.append(current_lesson)
            
            # Score lessons by relevance
            scored = []
            for lesson in lessons:
                lesson_text = f"{lesson.get('lesson', '')} {lesson.get('context', '')} {lesson.get('tags', '')}".lower()
                score = sum(1 for kw in keywords if kw in lesson_text and len(kw) > 3)
                if score > 0:
                    scored.append((score, lesson))
            
            # Return top lessons
            scored.sort(reverse=True, key=lambda x: x[0])
            return [l for _, l in scored[:max_lessons]]
            
    except:
        pass
    
    return []


def load_relevant_mistakes(prompt: str, max_mistakes: int = 2) -> list:
    """Load mistakes to avoid based on prompt."""
    mistakes = []
    
    try:
        mistakes_file = memory_dir / 'mistakes.yaml'
        if mistakes_file.exists():
            content = mistakes_file.read_text()
            
            prompt_lower = prompt.lower()
            keywords = set(prompt_lower.split())
            
            current_mistake = {}
            for line in content.split('\n'):
                if line.strip().startswith('- id:'):
                    if current_mistake and 'mistake' in current_mistake:
                        mistakes.append(current_mistake)
                    current_mistake = {'id': line.split(':', 1)[1].strip()}
                elif ':' in line and current_mistake:
                    key, value = line.strip().split(':', 1)
                    key = key.strip().lstrip('- ')
                    current_mistake[key] = value.strip().strip('"\'')
            
            if current_mistake and 'mistake' in current_mistake:
                mistakes.append(current_mistake)
            
            # Score by relevance
            scored = []
            for mistake in mistakes:
                mistake_text = f"{mistake.get('mistake', '')} {mistake.get('prevention', '')}".lower()
                score = sum(1 for kw in keywords if kw in mistake_text and len(kw) > 3)
                if score > 0:
                    scored.append((score, mistake))
            
            scored.sort(reverse=True, key=lambda x: x[0])
            return [m for _, m in scored[:max_mistakes]]
            
    except:
        pass
    
    return []


def get_workflow_context() -> str:
    """Get current workflow state context."""
    try:
        from workflow_state import WorkflowState
        ws = WorkflowState()
        return ws.get_summary()
    except:
        pass
    
    return ""


def get_project_context() -> str:
    """Get current project context."""
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        return ci.get_project_summary()
    except:
        pass
    
    return ""


def detect_task_complexity(prompt: str) -> str:
    """
    Detect task complexity from prompt to auto-adjust workflow depth.
    Returns: 'simple', 'medium', or 'complex'
    """
    prompt_lower = prompt.lower()
    
    # Complex task indicators
    complex_indicators = [
        'build', 'create new', 'implement system', 'full stack',
        'api and ui', 'frontend and backend', 'multiple services',
        'microservices', 'authentication system', 'complete feature',
        'from scratch', 'entire', 'comprehensive', 'enterprise',
        'database and api', 'full implementation'
    ]
    
    # Multi-domain indicators (needs architecture)
    multi_domain = [
        ('api', 'ui'), ('frontend', 'backend'), ('database', 'service'),
        ('auth', 'api'), ('component', 'service'), ('model', 'controller')
    ]
    
    # Simple task indicators
    simple_indicators = [
        'fix typo', 'rename', 'update comment', 'change text',
        'small fix', 'quick change', 'minor', 'simple'
    ]
    
    # Check for simple tasks first
    for indicator in simple_indicators:
        if indicator in prompt_lower:
            return 'simple'
    
    # Check for complex indicators
    complex_score = 0
    for indicator in complex_indicators:
        if indicator in prompt_lower:
            complex_score += 2
    
    # Check for multi-domain
    for d1, d2 in multi_domain:
        if d1 in prompt_lower and d2 in prompt_lower:
            complex_score += 3
    
    # Word count as complexity indicator
    word_count = len(prompt.split())
    if word_count > 50:
        complex_score += 1
    if word_count > 100:
        complex_score += 2
    
    if complex_score >= 4:
        return 'complex'
    elif complex_score >= 1:
        return 'medium'
    else:
        return 'simple'


def get_workflow_recommendation(complexity: str, prompt: str) -> str:
    """Get IMPERATIVE workflow instruction based on complexity.
    
    Factory AI needs explicit Task() calls, not just recommendations.
    This output goes into additionalContext which the main agent sees.
    """
    task_summary = prompt[:100] + "..." if len(prompt) > 100 else prompt
    
    if complexity == 'simple':
        return f"""⚡ DROIDPARTMENT WORKFLOW (Simple Task):
YOU MUST USE THESE EXACT TASK CALLS IN ORDER:

1. Task(subagent_type: "dpt-memory", prompt: "START: {task_summary}")
2. Task(subagent_type: "dpt-dev", prompt: "[implement the task]")
3. Task(subagent_type: "dpt-qa", prompt: "[verify implementation]")
4. Task(subagent_type: "dpt-memory", prompt: "END: [lessons learned]")
5. Task(subagent_type: "dpt-output", prompt: "summarize results")

DO NOT skip these steps. DO NOT implement directly without calling dpt-dev."""

    elif complexity == 'complex':
        return f"""🚀 DROIDPARTMENT WORKFLOW (Complex Task - Full Spec Required):
YOU MUST USE THESE EXACT TASK CALLS IN ORDER:

Wave 1 - Initialize:
1. Task(subagent_type: "dpt-memory", prompt: "START: {task_summary}")
2. Task(subagent_type: "dpt-research", prompt: "research best practices for this task")

Wave 2 - Specification:
3. Task(subagent_type: "dpt-product", prompt: "create PRD.md with requirements")

Wave 3 - Architecture:
4. Task(subagent_type: "dpt-arch", prompt: "create ARCHITECTURE.md based on PRD")

Wave 4 - Task Breakdown:
5. Task(subagent_type: "dpt-scrum", prompt: "break down into stories with [P]/[S] markers")

Wave 5 - Implementation:
6. Task(subagent_type: "dpt-dev", prompt: "[implement each component]")

Wave 6 - Quality (run these in parallel):
7. Task(subagent_type: "dpt-qa", prompt: "test implementation")
8. Task(subagent_type: "dpt-sec", prompt: "security audit")
9. Task(subagent_type: "dpt-lead", prompt: "code review")

Wave 7 - Finalize:
10. Task(subagent_type: "dpt-memory", prompt: "END: capture all lessons learned")
11. Task(subagent_type: "dpt-output", prompt: "synthesize final report")

⚠️ DO NOT skip waves. DO NOT implement directly. Follow this workflow."""

    else:  # medium
        return f"""📋 DROIDPARTMENT WORKFLOW (Medium Task):
YOU MUST USE THESE EXACT TASK CALLS IN ORDER:

1. Task(subagent_type: "dpt-memory", prompt: "START: {task_summary}")
2. Task(subagent_type: "dpt-scrum", prompt: "break down task into steps")
3. Task(subagent_type: "dpt-dev", prompt: "[implement based on breakdown]")
4. Task(subagent_type: "dpt-qa", prompt: "verify implementation")
5. Task(subagent_type: "dpt-memory", prompt: "END: lessons learned")
6. Task(subagent_type: "dpt-output", prompt: "summarize results")

DO NOT skip these steps. Call each agent in sequence."""


def should_auto_spec(prompt: str, complexity: str) -> bool:
    """Determine if task should auto-trigger spec creation."""
    if complexity != 'complex':
        return False
    
    prompt_lower = prompt.lower()
    
    # Spec-worthy indicators
    spec_triggers = [
        'new feature', 'new system', 'build', 'create application',
        'implement from', 'design and build', 'full implementation',
        'requirements', 'user story', 'acceptance criteria'
    ]
    
    return any(trigger in prompt_lower for trigger in spec_triggers)


def build_context_injection(prompt: str) -> str:
    """Build context string to inject."""
    parts = []
    
    # Scale-Adaptive: Detect task complexity and INSTRUCT workflow
    complexity = detect_task_complexity(prompt)
    workflow_instruction = get_workflow_recommendation(complexity, prompt)
    parts.append(workflow_instruction)
    
    # Auto-Spec: If complex task needs spec first
    if should_auto_spec(prompt, complexity):
        parts.append("[AUTO-SPEC: This task requires specification first. Call dpt-product before implementation.]")
    
    # Get relevant lessons
    lessons = load_relevant_lessons(prompt)
    if lessons:
        lesson_strs = []
        for l in lessons:
            lesson_strs.append(f"• {l.get('lesson', 'Unknown')}")
        parts.append(f"[Relevant lessons: {'; '.join(lesson_strs)}]")
    
    # Get mistakes to avoid
    mistakes = load_relevant_mistakes(prompt)
    if mistakes:
        mistake_strs = []
        for m in mistakes:
            mistake_strs.append(f"• Avoid: {m.get('mistake', 'Unknown')} - {m.get('prevention', '')}")
        parts.append(f"[Mistakes to avoid: {'; '.join(mistake_strs)}]")
    
    # Get workflow state
    workflow = get_workflow_context()
    if workflow:
        parts.append(workflow)
    
    # Get project context
    project = get_project_context()
    if project:
        parts.append(f"[{project}]")
    
    return ' '.join(parts) if parts else ''


def main():
    try:
        # Read input from Droid (Factory AI UserPromptSubmit format)
        input_data = json.load(sys.stdin)
        
        prompt = input_data.get('prompt', '')
        
        # Build context to inject
        additional_context = build_context_injection(prompt)
        
        # Only output if we have context to add
        if additional_context:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": additional_context
                }
            }
            print(json.dumps(output))
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        # Silent fail - don't interrupt Droid
        sys.exit(0)


if __name__ == '__main__':
    main()
