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
    """Record agent output to shared context."""
    try:
        from shared_context import SharedContext
        sc = SharedContext()
        
        # Extract summary from transcript if available
        summary = None
        if transcript_path:
            try:
                content = Path(transcript_path).read_text(errors='ignore')
                # Look for result/summary patterns
                recent = content[-3000:]
                if 'value:' in recent:
                    match = re.search(r'value:\s*["\']?([^"\'}\n]+)', recent)
                    if match:
                        summary = match.group(1)[:500]  # Limit length
            except:
                pass
        
        sc.record_agent_output(agent or 'unknown', summary or 'completed')
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
    """Update droid usage statistics."""
    try:
        stats_file = memory_dir / 'droid_usage.json'
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {'total_calls': 0, 'droids': {}, 'sessions': []}
        
        stats['total_calls'] += 1
        stats['last_call'] = datetime.now().isoformat()
        
        if agent:
            if agent not in stats['droids']:
                stats['droids'][agent] = 0
            stats['droids'][agent] += 1
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
            
    except:
        pass

def update_session_state(agent):
    """Update session state with agent completion."""
    try:
        session_file = memory_dir / 'session_state.json'
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                state = json.load(f)
        else:
            state = {'agents_run': [], 'droid_stats': {}}
        
        if 'agents_run' not in state:
            state['agents_run'] = []
        if 'droid_stats' not in state:
            state['droid_stats'] = {}
        
        state['agents_run'].append({
            'agent': agent or 'unknown',
            'completed_at': datetime.now().isoformat()
        })
        
        if agent:
            if agent not in state['droid_stats']:
                state['droid_stats'][agent] = 0
            state['droid_stats'][agent] += 1
        
        with open(session_file, 'w') as f:
            json.dump(state, f, indent=2)
            
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
    """Record extracted mistakes to project memory."""
    if not mistakes:
        return
    
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        current_project = ci.index.get('current_project')
        
        if current_project:
            for mistake in mistakes:
                mistake['prevention'] = f"Review before completing: {mistake.get('description', '')[:50]}"
                ci.record_mistake(current_project, mistake)
    except:
        pass

def refresh_project_index_if_needed():
    """Refresh project index if files were changed during agent run."""
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        
        # Check if re-index is needed
        if ci.index.get('needs_reindex'):
            current_project = ci.index.get('current_project')
            if current_project:
                # Re-initialize project memory
                ci.initialize_project_memory(current_project)
                ci.index['needs_reindex'] = False
                ci._save_index()
    except:
        pass

def main():
    try:
        # Read input from Droid (Factory AI SubagentStop format)
        input_data = json.load(sys.stdin)
        
        session_id = input_data.get('session_id', 'unknown')
        transcript_path = input_data.get('transcript_path', '')
        stop_hook_active = input_data.get('stop_hook_active', False)
        
        # Prevent infinite loop - if stop_hook_active, just exit
        if stop_hook_active:
            sys.exit(0)
        
        # Extract agent info from transcript
        agent = extract_agent_from_transcript(transcript_path)
        next_agent = extract_next_agent_signal(transcript_path)
        
        # Record agent output and update state
        record_agent_output(agent, transcript_path)
        update_workflow_state(agent)
        update_droid_stats(agent)
        update_session_state(agent)
        
        # Extract and record any mistakes from agent output
        mistakes = extract_mistakes_from_transcript(transcript_path, agent)
        if mistakes:
            record_agent_mistakes(mistakes)
        
        # Refresh project index if files changed during agent run
        refresh_project_index_if_needed()
        
        # Check if we should continue loop (brainstorm mode)
        if should_continue_loop():
            # Return decision:block to make Droid continue
            output = {
                "decision": "block",
                "reason": f"Brainstorm iteration in progress. Continue with refinement. Last agent: {agent or 'unknown'}. Consider running next iteration or review."
            }
            print(json.dumps(output))
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
        
        # Normal exit - allow subagent to stop
        sys.exit(0)
        
    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        sys.exit(0)

if __name__ == '__main__':
    main()
