#!/usr/bin/env python3
"""
Factory Droid Hook: SubagentStop (Enhanced v3)
Triggers when a sub-agent (dpt-dev, dpt-qa, dpt-sec, etc.) completes.

Features:
- Context passing between agents
- Loop/brainstorm capability via decision:block
- Droid usage tracking
- Workflow state updates
- Mistake extraction and recording to project memory
- Project index refresh on file changes

Input: JSON from stdin with session_id, transcript_path, stop_hook_active
Output: JSON with optional decision:block to continue iteration
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Add memory directory to path for imports
memory_dir = Path(os.path.expanduser('~/.factory/memory'))
sys.path.insert(0, str(memory_dir))

# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE OPTIMIZATION: Singleton cache for expensive objects
# ═══════════════════════════════════════════════════════════════════════════════
_cache = {
    'context_index': None,
    'droid_stats': None,
    'droid_stats_dirty': False,
    'session_state': None,
    'session_dirty': False
}

def get_context_index():
    """Get cached ContextIndex singleton with lazy loading."""
    if _cache['context_index'] is None:
        try:
            from context_index import ContextIndex
            _cache['context_index'] = ContextIndex()
        except:
            pass
    return _cache['context_index']

def clear_cache(key: str = None):
    """Clear specific cache entry or all if key is None."""
    import gc
    if key is None:
        for k in list(_cache.keys()):
            if not k.endswith('_dirty'):
                _cache[k] = None
        gc.collect()
    elif key in _cache:
        _cache[key] = None
        gc.collect()

def get_droid_stats():
    """Get cached droid stats."""
    if _cache['droid_stats'] is None:
        stats_file = memory_dir / 'droid_usage.json'
        try:
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    _cache['droid_stats'] = json.load(f)
            else:
                _cache['droid_stats'] = {'total_calls': 0, 'droids': {}, 'sessions': []}
        except:
            _cache['droid_stats'] = {'total_calls': 0, 'droids': {}, 'sessions': []}
    return _cache['droid_stats']

def get_session_state():
    """Get cached session state."""
    if _cache['session_state'] is None:
        session_file = memory_dir / 'session_state.json'
        try:
            if session_file.exists():
                with open(session_file, 'r') as f:
                    _cache['session_state'] = json.load(f)
            else:
                _cache['session_state'] = {'agents_run': [], 'droid_stats': {}, 'workflow_tracking': {}}
        except:
            _cache['session_state'] = {'agents_run': [], 'droid_stats': {}, 'workflow_tracking': {}}
    return _cache['session_state']

def save_all_caches():
    """Save all dirty caches before exit."""
    if _cache['droid_stats_dirty'] and _cache['droid_stats']:
        try:
            with open(memory_dir / 'droid_usage.json', 'w') as f:
                json.dump(_cache['droid_stats'], f, indent=2)
        except:
            pass
    if _cache['session_dirty'] and _cache['session_state']:
        try:
            with open(memory_dir / 'session_state.json', 'w') as f:
                json.dump(_cache['session_state'], f, indent=2)
        except:
            pass

def extract_agent_from_transcript(transcript_path):
    """Try to extract droid name from transcript."""
    if not transcript_path:
        return None
    
    try:
        transcript_file = Path(transcript_path)
        if transcript_file.exists():
            content = transcript_file.read_text(errors='ignore')
            # Look for dpt-* pattern in recent content (last 10KB)
            recent = content[-10000:] if len(content) > 10000 else content
            droids = re.findall(r'dpt-\w+', recent)
            if droids:
                return droids[-1]  # Most recent droid
    except:
        pass
    return None

def extract_next_agent_signal(transcript_path):
    """Extract next_agent signal from transcript if present."""
    if not transcript_path:
        return None
    
    try:
        transcript_file = Path(transcript_path)
        if transcript_file.exists():
            content = transcript_file.read_text(errors='ignore')
            recent = content[-5000:]  # Check last 5KB
            
            # Look for next_agent patterns
            patterns = [
                r'next_agent["\s:]+["\']?(dpt-\w+)',
                r'next_agent:\s*(dpt-\w+)',
                r'"next_agent":\s*"(dpt-\w+)"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, recent)
                if matches:
                    return matches[-1]
    except:
        pass
    return None

def should_continue_loop():
    """Check if brainstorm/iteration loop should continue."""
    try:
        from workflow_state import WorkflowState
        ws = WorkflowState()
        return ws.should_loop()
    except ImportError:
        # Fallback check
        try:
            state_file = memory_dir / 'workflow_state.json'
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                if state.get('brainstorm_active'):
                    return state.get('iteration_count', 0) < state.get('max_iterations', 5)
        except:
            pass
    return False

def record_agent_output(agent, transcript_path):
    """Record agent output to shared context with full content extraction."""
    try:
        from shared_context import SharedContext
        sc = SharedContext()
        
        # Extract full output from transcript
        output = None
        if transcript_path:
            try:
                content = Path(transcript_path).read_text(errors='ignore')
                
                # Try multiple extraction patterns (from most to least specific)
                
                # Pattern 1: Look for "Summary:" section (common in dpt-* agents)
                if 'Summary:' in content:
                    match = re.search(r'Summary:\s*(.+?)(?:\n\n|\nFindings:|\nFollow-up:|\Z)', content, re.DOTALL)
                    if match:
                        output = match.group(1).strip()[:2000]
                
                # Pattern 2: Look for "Findings:" section
                if not output and 'Findings:' in content:
                    match = re.search(r'Findings:\s*(.+?)(?:\n\nFollow-up:|\n\nNext|\Z)', content, re.DOTALL)
                    if match:
                        output = match.group(1).strip()[:2000]
                
                # Pattern 3: Look for last assistant message
                if not output:
                    # Find last substantial text block (after last "assistant" role)
                    parts = content.split('assistant')
                    if len(parts) > 1:
                        last_part = parts[-1][:3000]
                        # Clean up and take meaningful content
                        lines = [l.strip() for l in last_part.split('\n') if l.strip() and len(l.strip()) > 20]
                        if lines:
                            output = '\n'.join(lines[:30])  # First 30 meaningful lines
                
                # Pattern 4: Last resort - take recent content
                if not output:
                    recent = content[-2000:]
                    if 'value:' in recent:
                        match = re.search(r'value:\s*["\']?([^"\'}\n]+)', recent)
                        if match:
                            output = match.group(1)[:500]
                
            except:
                pass
        
        # Record with extracted output or "completed"
        sc.record_agent_output(agent or 'unknown', output or 'completed')
        
        # Also save to a dedicated agent outputs file for dpt-output to read
        try:
            outputs_file = memory_dir / 'agent_outputs.json'
            outputs = {}
            if outputs_file.exists():
                with open(outputs_file, 'r') as f:
                    outputs = json.load(f)
            
            outputs[agent or 'unknown'] = {
                'output': output or 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
            with open(outputs_file, 'w') as f:
                json.dump(outputs, f, indent=2)
        except:
            pass
        
        return True
    except ImportError:
        pass
    except:
        pass
    return False

def update_workflow_state(agent):
    """Update workflow state based on agent."""
    try:
        from workflow_state import WorkflowState, infer_state_from_agent
        ws = WorkflowState()
        
        # Infer state from agent
        if agent:
            inferred = infer_state_from_agent(agent)
            if ws.can_transition(inferred):
                ws.transition(inferred, f'Agent {agent} completed')
        
        ws.record_agent_output(agent or 'unknown', 'completed')
        return ws.get_summary()
    except ImportError:
        return None
    except:
        return None

def update_droid_stats(agent):
    """Update droid usage statistics (uses cache)."""
    try:
        stats = get_droid_stats()
        stats['total_calls'] = stats.get('total_calls', 0) + 1
        stats['last_call'] = datetime.now().isoformat()
        
        if agent:
            if 'droids' not in stats:
                stats['droids'] = {}
            if agent not in stats['droids']:
                stats['droids'][agent] = 0
            stats['droids'][agent] += 1
        
        _cache['droid_stats_dirty'] = True
    except:
        pass

def update_session_state(agent):
    """Update session state with agent completion (uses cache)."""
    try:
        state = get_session_state()
        
        if 'agents_run' not in state:
            state['agents_run'] = []
        if 'droid_stats' not in state:
            state['droid_stats'] = {}
        if 'workflow_tracking' not in state:
            state['workflow_tracking'] = {
                'memory_start_called': False,
                'memory_end_called': False,
                'output_called': False,
                'lessons_captured': False
            }
        
        state['agents_run'].append({
            'agent': agent or 'unknown',
            'completed_at': datetime.now().isoformat()
        })
        
        if agent:
            if agent not in state['droid_stats']:
                state['droid_stats'][agent] = 0
            state['droid_stats'][agent] += 1
            
            # Track critical workflow steps
            if agent == 'dpt-memory':
                # Check if this is START or END by looking at recent agents
                agents_list = [a.get('agent') for a in state['agents_run']]
                if len(agents_list) <= 2:  # Early in workflow
                    state['workflow_tracking']['memory_start_called'] = True
                else:
                    state['workflow_tracking']['memory_end_called'] = True
                    state['workflow_tracking']['lessons_captured'] = True
            elif agent == 'dpt-output':
                state['workflow_tracking']['output_called'] = True
        
        _cache['session_dirty'] = True
    except:
        pass

def extract_mistakes_from_transcript(transcript_path, agent):
    """Extract mistakes mentioned in agent output."""
    if not transcript_path:
        return []
    
    mistakes = []
    try:
        transcript_file = Path(transcript_path)
        if transcript_file.exists():
            content = transcript_file.read_text(errors='ignore')
            recent = content[-10000:]  # Check last 10KB
            
            # Patterns that indicate mistakes
            mistake_patterns = [
                r'(?:mistake|error|bug|issue|problem|wrong|incorrect|failed).*?:?\s*(.{20,100})',
                r'should have\s+(.{20,80})',
                r'forgot to\s+(.{20,80})',
                r'missed\s+(.{20,80})',
                r'overlooked\s+(.{20,80})',
            ]
            
            for pattern in mistake_patterns:
                matches = re.findall(pattern, recent, re.IGNORECASE)
                for match in matches[:2]:  # Limit to 2 per pattern
                    if len(match) > 20:  # Only meaningful matches
                        mistakes.append({
                            'agent': agent,
                            'description': match.strip()[:100],
                            'context': 'Extracted from agent output',
                            'severity': 'low'
                        })
    except:
        pass
    
    return mistakes[:3]  # Max 3 mistakes per agent run

def record_agent_mistakes(mistakes):
    """DEPRECATED: Use record_agent_mistakes_to_project instead."""
    pass

def record_agent_mistakes_to_project(cwd: str, mistakes):
    """
    Record extracted mistakes to PROJECT-SPECIFIC memory (uses cache).
    Uses cwd directly instead of relying on current_project in index.
    """
    if not mistakes:
        return
    
    ci = get_context_index()
    if ci:
        try:
            for mistake in mistakes:
                mistake['prevention'] = f"Review before completing: {mistake.get('description', '')[:50]}"
                ci.record_mistake(cwd, mistake)
        except:
            pass

def refresh_project_index_if_needed(cwd: str = None):
    """
    Refresh project index if files were changed during agent run (uses cache).
    Uses cwd directly instead of relying on current_project in index.
    """
    ci = get_context_index()
    if ci:
        try:
            # Check if re-index is needed
            if ci.index.get('needs_reindex'):
                project_path = cwd or ci.index.get('current_project')
                if project_path:
                    # Re-initialize project memory
                    ci.initialize_project_memory(project_path)
                    ci.index['needs_reindex'] = False
                    ci._save_index()
        except:
            pass


def check_workflow_completion(agent):
    """
    LEARNING SYSTEM: Check if workflow is complete and lessons were captured (uses cache).
    This is the "verification layer" that detects skipped steps.
    
    Returns: (is_complete, warning_message)
    """
    try:
        state = get_session_state()
        if not state:
            return True, None
        
        tracking = state.get('workflow_tracking', {})
        
        # If dpt-output just ran, verify dpt-memory END was called
        if agent == 'dpt-output':
            if not tracking.get('memory_end_called', False):
                # PENALTY: Record this as a workflow mistake
                record_workflow_mistake({
                    'agent': 'workflow',
                    'description': 'dpt-memory END was skipped before dpt-output',
                    'context': 'No lessons were captured from this session',
                    'severity': 'high',
                    'prevention': 'Always call dpt-memory END before dpt-output to capture lessons'
                })
                
                # Return warning to inject into context
                return False, """
⚠️ WORKFLOW INCOMPLETE: dpt-memory END was SKIPPED!

No lessons were captured from this session.
The learning system cannot improve without END calls.

You MUST call: Task(subagent_type: "dpt-memory", prompt: "END: [what was learned]")

This mistake has been recorded for learning.
"""
        
        return True, None
    except:
        return True, None


def record_workflow_mistake(mistake):
    """Record a workflow-level mistake for learning."""
    try:
        # Record to global mistakes file
        mistakes_file = memory_dir / 'mistakes.yaml'
        
        entry = f"""
- id: workflow_{datetime.now().strftime('%Y%m%d%H%M%S')}
  date: {datetime.now().isoformat()}
  agent: {mistake.get('agent', 'workflow')}
  mistake: "{mistake.get('description', 'Unknown workflow mistake')}"
  context: "{mistake.get('context', '')}"
  prevention: "{mistake.get('prevention', 'Follow the complete workflow')}"
  severity: {mistake.get('severity', 'medium')}
"""
        
        with open(mistakes_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # Also record to project-specific mistakes if project is known (use cached ctx)
        ci = get_context_index()
        if ci:
            try:
                current_project = ci.index.get('current_project')
                if current_project:
                    ci.record_mistake(current_project, mistake)
            except:
                pass
            
    except:
        pass


def get_lessons_reminder():
    """Get a reminder about capturing lessons if END was skipped (uses cache)."""
    try:
        state = get_session_state()
        if not state:
            return None
        
        tracking = state.get('workflow_tracking', {})
        
        # If output was called but END wasn't, remind about lessons
        if tracking.get('output_called') and not tracking.get('lessons_captured'):
            return """
🧠 REMINDER: No lessons captured this session!

Call dpt-memory END to record what was learned.
This improves the system for future sessions.
"""
        
        return None
    except:
        return None

def main():
    try:
        # Read input from Droid (Factory AI SubagentStop format)
        input_data = json.load(sys.stdin)
        
        session_id = input_data.get('session_id', 'unknown')
        transcript_path = input_data.get('transcript_path', '')
        stop_hook_active = input_data.get('stop_hook_active', False)
        cwd = input_data.get('cwd', os.getcwd())  # Get cwd from input (per Factory AI docs)
        
        # Prevent infinite loop - if stop_hook_active, just exit
        if stop_hook_active:
            save_all_caches()
            sys.exit(0)
        
        # Get agent from SharedContext first (set by PreToolUse - more reliable)
        agent = None
        try:
            from shared_context import SharedContext
            sc = SharedContext()
            agent = sc.context.get('agents', {}).get('current')
            # Clear current agent since this one is now stopping
            if agent:
                sc.context['agents']['current'] = None
                sc._save_context()
        except:
            pass
        
        # Fallback: Extract agent info from transcript (less reliable)
        if not agent:
            agent = extract_agent_from_transcript(transcript_path)
        next_agent = extract_next_agent_signal(transcript_path)
        
        # Record agent output and update state
        record_agent_output(agent, transcript_path)
        update_workflow_state(agent)
        update_droid_stats(agent)
        update_session_state(agent)
        
        # Extract and record any mistakes from agent output (PROJECT-SPECIFIC)
        mistakes = extract_mistakes_from_transcript(transcript_path, agent)
        if mistakes:
            record_agent_mistakes_to_project(cwd, mistakes)
        
        # Refresh project index if files changed during agent run
        refresh_project_index_if_needed(cwd)
        
        # ============= LEARNING SYSTEM: VERIFICATION LAYER =============
        # Check if dpt-output ran without dpt-memory END (lesson capture)
        is_complete, warning_message = check_workflow_completion(agent)
        
        if not is_complete and warning_message:
            # PENALTY SIGNAL: Inject warning and block to force correction
            output = {
                "decision": "block",
                "reason": warning_message
            }
            print(json.dumps(output))
            save_all_caches()
            sys.exit(0)
        # ================================================================
        
        # Check if we should continue loop (brainstorm mode)
        if should_continue_loop():
            # Return decision:block to make Droid continue
            output = {
                "decision": "block",
                "reason": f"Brainstorm iteration in progress. Continue with refinement. Last agent: {agent or 'unknown'}. Consider running next iteration or review."
            }
            print(json.dumps(output))
            save_all_caches()
            sys.exit(0)
        
        # Check if next_agent was signaled
        if next_agent and next_agent != agent:
            try:
                from shared_context import SharedContext
                sc = SharedContext()
                sc.add_handoff(agent or 'unknown', next_agent, {
                    'signal': 'next_agent',
                    'timestamp': datetime.now().isoformat()
                })
            except:
                pass
        
        # Save all cached data before normal exit
        save_all_caches()
        sys.exit(0)
        
    except json.JSONDecodeError:
        save_all_caches()
        sys.exit(0)
    except Exception as e:
        save_all_caches()
        sys.exit(0)

if __name__ == '__main__':
    main()
