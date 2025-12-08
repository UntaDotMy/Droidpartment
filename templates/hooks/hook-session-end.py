#!/usr/bin/env python3
"""
Factory Droid Hook: SessionEnd (Enhanced v3)
Triggers when Droid session ends.

Features:
- Session Persistence for long workflow resume
- Auto-save incomplete tasks for continuation
- Save final statistics
- Archive session data
- Process captured errors into lessons
- Delta change summary
- Cleanup temporary files
- Persist workflow state

Input: JSON from stdin with session_id, reason
Output: Exit 0 for success
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add memory directory to path for imports
memory_dir = Path(os.path.expanduser('~/.factory/memory'))
sys.path.insert(0, str(memory_dir))

def save_session_summary():
    """Save session summary to history."""
    try:
        session_file = memory_dir / 'session_state.json'
        tool_stats_file = memory_dir / 'tool_stats.json'
        droid_usage_file = memory_dir / 'droid_usage.json'
        
        # Collect session data
        session_data = {}
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        
        tool_stats = {}
        if tool_stats_file.exists():
            with open(tool_stats_file, 'r') as f:
                tool_stats = json.load(f)
        
        droid_stats = {}
        if droid_usage_file.exists():
            with open(droid_usage_file, 'r') as f:
                droid_stats = json.load(f)
        
        # Create session summary
        summary = {
            'ended_at': datetime.now().isoformat(),
            'started_at': session_data.get('started_at'),
            'tools_used': session_data.get('tools_used', 0),
            'agents_run': len(session_data.get('agents_run', [])),
            'droids_called': droid_stats.get('total_calls', 0),
            'droid_breakdown': droid_stats.get('droids', {}),
            'tool_breakdown': tool_stats.get('tools', {}),
            'errors': tool_stats.get('errors', 0)
        }
        
        # Save to history
        history_file = memory_dir / 'session_history.json'
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {'sessions': []}
        
        history['sessions'].append(summary)
        
        # Keep only last 50 sessions
        if len(history['sessions']) > 50:
            history['sessions'] = history['sessions'][-50:]
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return True
    except:
        return False

def process_errors_to_lessons():
    """Process captured errors into potential lessons."""
    try:
        errors_file = memory_dir / 'captured_errors.json'
        
        if not errors_file.exists():
            return
        
        with open(errors_file, 'r') as f:
            errors_data = json.load(f)
        
        patterns = errors_data.get('patterns', {})
        
        # Find recurring patterns (3+ occurrences)
        recurring = {k: v for k, v in patterns.items() if v >= 3}
        
        if not recurring:
            return
        
        # Record as potential lessons
        potential_lessons_file = memory_dir / 'potential_lessons.json'
        
        if potential_lessons_file.exists():
            with open(potential_lessons_file, 'r') as f:
                potential = json.load(f)
        else:
            potential = {'lessons': []}
        
        for error_type, count in recurring.items():
            lesson = {
                'type': 'error_pattern',
                'pattern': error_type,
                'occurrences': count,
                'suggestion': f'Recurring {error_type} errors detected ({count} times). Consider adding prevention strategy.',
                'captured_at': datetime.now().isoformat()
            }
            
            # Check if already recorded
            existing = [l for l in potential['lessons'] if l.get('pattern') == error_type]
            if not existing:
                potential['lessons'].append(lesson)
        
        with open(potential_lessons_file, 'w') as f:
            json.dump(potential, f, indent=2)
            
    except:
        pass

def cleanup_temp_files(keep_errors=True):
    """Cleanup temporary session files."""
    try:
        # Files to clean
        temp_files = [
            'session_state.json',
            'tool_stats.json',
            'agent_context.json',
            'files_modified.json'
        ]
        
        # Optionally keep errors for learning
        if not keep_errors:
            temp_files.append('captured_errors.json')
        
        for temp_file in temp_files:
            file_path = memory_dir / temp_file
            if file_path.exists():
                file_path.unlink()
        
        return True
    except:
        return False

def reset_workflow_state():
    """Reset workflow state for next session."""
    try:
        from workflow_state import WorkflowState
        ws = WorkflowState()
        
        # Save final state before reset
        final_state = {
            'last_state': ws.get_state(),
            'iterations': ws.state.get('iteration_count', 0),
            'ended_at': datetime.now().isoformat()
        }
        
        # Archive to history
        workflow_history_file = memory_dir / 'workflow_history.json'
        if workflow_history_file.exists():
            with open(workflow_history_file, 'r') as f:
                history = json.load(f)
        else:
            history = {'sessions': []}
        
        history['sessions'].append(final_state)
        if len(history['sessions']) > 50:
            history['sessions'] = history['sessions'][-50:]
        
        with open(workflow_history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        # Reset for next session
        ws.reset()
        
    except ImportError:
        pass
    except:
        pass

def reset_shared_context():
    """Reset shared context for next session."""
    try:
        from shared_context import SharedContext
        sc = SharedContext()
        sc.reset()
    except ImportError:
        pass
    except:
        pass


def save_session_for_resume(session_id: str, reason: str):
    """
    Save session state for potential resume.
    Enables long-running workflow continuation.
    """
    try:
        sessions_dir = memory_dir / 'sessions'
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect current state
        session_state = {}
        
        # Get workflow state
        try:
            from workflow_state import WorkflowState
            ws = WorkflowState()
            session_state['workflow'] = ws.get_state()
            session_state['pending_tasks'] = ws.state.get('pending_tasks', [])
            session_state['completed_agents'] = ws.state.get('agents_completed', [])
        except:
            pass
        
        # Get shared context (agent outputs)
        try:
            from shared_context import SharedContext
            sc = SharedContext()
            session_state['agent_outputs'] = sc.context.get('agent_outputs', {})
            session_state['handoffs'] = sc.context.get('handoffs', [])
        except:
            pass
        
        # Get current project
        try:
            from context_index import ContextIndex
            ci = ContextIndex()
            session_state['project_path'] = ci.index.get('current_project')
        except:
            pass
        
        # Get files modified in this session
        files_modified_file = memory_dir / 'files_modified.json'
        if files_modified_file.exists():
            with open(files_modified_file, 'r') as f:
                session_state['files_modified'] = json.load(f)
        
        # Check if there are incomplete tasks
        has_incomplete = bool(session_state.get('pending_tasks'))
        
        # Save session
        resume_data = {
            'session_id': session_id,
            'saved_at': datetime.now().isoformat(),
            'exit_reason': reason,
            'has_incomplete_tasks': has_incomplete,
            'state': session_state
        }
        
        # Save to session file
        session_file = sessions_dir / f'{session_id}.json'
        with open(session_file, 'w') as f:
            json.dump(resume_data, f, indent=2)
        
        # Update active session pointer
        active_file = sessions_dir / 'active.json'
        with open(active_file, 'w') as f:
            json.dump({
                'session_id': session_id,
                'saved_at': datetime.now().isoformat(),
                'has_incomplete': has_incomplete,
                'project': session_state.get('project_path')
            }, f, indent=2)
        
        return True
    except:
        return False


def save_delta_summary():
    """
    Save a summary of all changes made during this session.
    For audit and review purposes.
    """
    try:
        files_modified_file = memory_dir / 'files_modified.json'
        if not files_modified_file.exists():
            return
        
        with open(files_modified_file, 'r') as f:
            files = json.load(f)
        
        if not files:
            return
        
        # Group by action
        created = [f for f, info in files.items() if info.get('action') == 'created']
        modified = [f for f, info in files.items() if info.get('action') == 'modified']
        
        # Create delta summary
        delta_summary = {
            'session_ended': datetime.now().isoformat(),
            'total_changes': len(files),
            'files_created': len(created),
            'files_modified': len(modified),
            'created_list': created[:20],  # Limit to 20
            'modified_list': modified[:20]
        }
        
        # Save to project memory if available
        try:
            from context_index import ContextIndex
            ci = ContextIndex()
            current_project = ci.index.get('current_project')
            
            if current_project:
                project_name = Path(current_project).name
                project_memory_dir = memory_dir / 'projects' / f"{project_name}_{hash(current_project) % 10000}"
                changes_dir = project_memory_dir / 'changes'
                changes_dir.mkdir(parents=True, exist_ok=True)
                
                # Save delta
                delta_file = changes_dir / f"delta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(delta_file, 'w') as f:
                    json.dump(delta_summary, f, indent=2)
        except:
            pass
        
    except:
        pass


def main():
    try:
        # Read input from Droid (Factory AI SessionEnd format)
        input_data = json.load(sys.stdin)
        
        session_id = input_data.get('session_id', 'unknown')
        reason = input_data.get('reason', 'exit')
        
        # Save session summary
        save_session_summary()
        
        # Save delta summary (track all changes made)
        save_delta_summary()
        
        # Save session for potential resume (long workflow continuation)
        save_session_for_resume(session_id, reason)
        
        # Process errors into potential lessons
        process_errors_to_lessons()
        
        # Only full cleanup on actual exit (not clear/compact)
        if reason in ['exit', 'logout', 'prompt_input_exit', 'other']:
            cleanup_temp_files(keep_errors=True)
            reset_workflow_state()
            reset_shared_context()
        
        # Exit 0 = success (cannot block session termination)
        sys.exit(0)
        
    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        sys.exit(0)

if __name__ == '__main__':
    main()
