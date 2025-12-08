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


def detect_task_type(prompt: str) -> dict:
    """
    Detect task complexity AND type using ML-inspired pattern recognition.
    Returns: {complexity: str, agents: list, domains: list, recognition_scores: dict}
    
    Uses PatternRecognizer for confidence-based agent selection (0.0 to 1.0).
    """
    prompt_lower = prompt.lower()
    
    # Use Pattern Recognition system
    try:
        from context_index import PatternRecognizer
        recognizer = PatternRecognizer()
        
        # Get recognition scores for all agents
        recognition_scores = recognizer.recognize_agents(prompt)
        
        # Start with recognized agents (sorted by confidence)
        agents = list(recognition_scores.keys())
        
        # Ensure dpt-memory is always first (critical agent)
        if 'dpt-memory' not in agents:
            agents.insert(0, 'dpt-memory')
        elif agents[0] != 'dpt-memory':
            agents.remove('dpt-memory')
            agents.insert(0, 'dpt-memory')
        
        # Ensure dpt-output is always included
        if 'dpt-output' not in agents:
            agents.append('dpt-output')
        
        # Record this recognition for learning
        recognizer.record_recognition(prompt, recognition_scores)
        
    except ImportError:
        # Fallback if PatternRecognizer not available
        recognition_scores = {}
        agents = ['dpt-memory', 'dpt-output']
    
    # Domain detection for complexity assessment
    domain_keywords = {
        'database': ['database', 'db', 'sql', 'query', 'schema', 'migration', 'table', 'model', 'orm'],
        'api': ['api', 'endpoint', 'rest', 'graphql', 'route', 'controller', 'http'],
        'ui': ['ui', 'ux', 'frontend', 'component', 'page', 'form', 'button', 'layout', 'css', 'style'],
        'devops': ['deploy', 'ci', 'cd', 'docker', 'kubernetes', 'pipeline', 'aws', 'azure'],
        'docs': ['document', 'readme', 'guide', 'tutorial', 'comment', 'jsdoc'],
        'performance': ['performance', 'optimize', 'speed', 'slow', 'cache', 'benchmark'],
        'security': ['security', 'auth', 'login', 'password', 'token', 'jwt', 'oauth', 'encrypt'],
    }
    
    detected_domains = []
    for domain_name, keywords in domain_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            detected_domains.append(domain_name)
    
    # Determine complexity based on recognition and domains
    complexity = 'medium'
    
    # Simple: Few agents recognized, low total confidence
    total_confidence = sum(recognition_scores.values())
    agent_count = len(recognition_scores)
    
    simple_indicators = ['fix typo', 'rename', 'update comment', 'small fix', 'quick change', 'minor', 'simple', 'tweak']
    complex_indicators = ['build', 'create new', 'implement system', 'full stack', 'from scratch', 'entire', 'comprehensive']
    
    if any(ind in prompt_lower for ind in simple_indicators):
        complexity = 'simple'
    elif any(ind in prompt_lower for ind in complex_indicators) or len(detected_domains) >= 2 or agent_count >= 6:
        complexity = 'complex'
        # Ensure complex tasks have core agents
        for core_agent in ['dpt-research', 'dpt-arch', 'dpt-scrum', 'dpt-dev', 'dpt-qa']:
            if core_agent not in agents:
                agents.append(core_agent)
    else:
        # Medium: ensure basic workflow agents
        for medium_agent in ['dpt-dev', 'dpt-qa']:
            if medium_agent not in agents:
                agents.append(medium_agent)
    
    # Always add review for non-simple tasks
    if complexity != 'simple' and 'dpt-review' not in agents:
        agents.append('dpt-review')
    
    # Remove duplicates while preserving order
    seen = set()
    unique_agents = []
    for agent in agents:
        if agent not in seen:
            seen.add(agent)
            unique_agents.append(agent)
    
    return {
        'complexity': complexity,
        'agents': unique_agents,
        'domains': detected_domains,
        'recognition_scores': recognition_scores  # Include scores for visibility
    }


def get_workflow_recommendation(task_info: dict, prompt: str) -> str:
    """Get MANDATORY workflow instruction based on detected task type and agents.
    
    This is NOT optional. Factory AI MUST follow these instructions.
    The output goes into additionalContext which the main agent sees.
    """
    complexity = task_info['complexity']
    agents = task_info['agents']
    domains = task_info.get('domains', [])
    recognition_scores = task_info.get('recognition_scores', {})
    
    task_summary = prompt[:100] + "..." if len(prompt) > 100 else prompt
    
    # Build domain string
    domain_str = f" (Domains: {', '.join(domains)})" if domains else ""
    
    # Build recognition scores visualization (ML-style confidence bars)
    score_lines = []
    if recognition_scores:
        score_lines.append("📊 AGENT RECOGNITION SCORES (ML confidence 0.0-1.0):")
        for agent, score in list(recognition_scores.items())[:8]:  # Top 8
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            score_lines.append(f"   {agent}: {bar} {score:.2f}")
    
    recognition_display = "\n".join(score_lines) if score_lines else ""
    
    mandatory_header = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🚨 MANDATORY: YOU MUST USE DROIDPARTMENT AGENTS FOR THIS TASK              ║
║                                                                              ║
║  DO NOT write code yourself. DO NOT analyze files yourself.                  ║
║  DO NOT skip Task() calls. DELEGATE EVERYTHING to dpt-* agents.              ║
║                                                                              ║
║  Your ONLY job is to call Task() with the appropriate agent.                 ║
║  The agents will do the actual work.                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

DETECTED: {complexity.upper()} task{domain_str}
AGENTS TO USE: {', '.join(agents)}

{recognition_display}
"""
    
    # Build dynamic workflow based on detected agents
    steps = []
    step_num = 1
    
    # Always start with dpt-memory
    steps.append(f'Step {step_num}: Task(subagent_type: "dpt-memory", prompt: "START: {task_summary}")')
    step_num += 1
    
    # Add research if detected
    if 'dpt-research' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-research", prompt: "research best practices")')
        step_num += 1
    
    # Add planning agents
    if 'dpt-product' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-product", prompt: "create PRD.md")')
        step_num += 1
    
    if 'dpt-arch' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-arch", prompt: "analyze/design architecture")')
        step_num += 1
    
    if 'dpt-scrum' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-scrum", prompt: "break down into tasks")')
        step_num += 1
    
    # Add domain-specific agents
    if 'dpt-data' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-data", prompt: "database design/queries")')
        step_num += 1
    
    if 'dpt-api' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-api", prompt: "API design/endpoints")')
        step_num += 1
    
    if 'dpt-ux' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-ux", prompt: "UI/UX design")')
        step_num += 1
    
    # Implementation
    if 'dpt-dev' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-dev", prompt: "[implement the work]")')
        step_num += 1
    
    # Quality/audit agents
    if 'dpt-qa' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-qa", prompt: "test/verify implementation")')
        step_num += 1
    
    if 'dpt-sec' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-sec", prompt: "security audit")')
        step_num += 1
    
    if 'dpt-perf' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-perf", prompt: "performance analysis")')
        step_num += 1
    
    if 'dpt-lead' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-lead", prompt: "code review")')
        step_num += 1
    
    if 'dpt-review' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-review", prompt: "simplicity check")')
        step_num += 1
    
    # DevOps
    if 'dpt-ops' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-ops", prompt: "deployment/CI setup")')
        step_num += 1
    
    # Documentation
    if 'dpt-docs' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-docs", prompt: "write documentation")')
        step_num += 1
    
    if 'dpt-grammar' in agents:
        steps.append(f'Step {step_num}: Task(subagent_type: "dpt-grammar", prompt: "improve writing quality")')
        step_num += 1
    
    # CRITICAL FINAL STEPS (order matters for learning system!)
    # Output FIRST (so user sees results), then END (to capture lessons)
    steps.append(f'Step {step_num}: Task(subagent_type: "dpt-output", prompt: "synthesize final report")')
    step_num += 1
    steps.append(f'Step {step_num}: ⚠️ REQUIRED - Task(subagent_type: "dpt-memory", prompt: "END: capture lessons learned") - DO NOT SKIP!')
    
    # Determine emoji based on complexity
    emoji = {'simple': '🟢', 'medium': '🟡', 'complex': '🔴'}.get(complexity, '🟡')
    
    workflow = f"""
{emoji} {complexity.upper()} TASK - Execute these {len(steps)} Task() calls:

{chr(10).join(steps)}

⛔ FORBIDDEN: Writing code yourself, skipping agents, analyzing files directly.
✅ REQUIRED: Call Task() for EVERY step. Start with Step 1 NOW."""
    
    return mandatory_header + workflow


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
    
    # Smart Task Detection: Detect complexity AND which agents to use
    task_info = detect_task_type(prompt)
    workflow_instruction = get_workflow_recommendation(task_info, prompt)
    parts.append(workflow_instruction)
    
    # Auto-Spec: If complex task needs spec first
    if should_auto_spec(prompt, task_info['complexity']):
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
