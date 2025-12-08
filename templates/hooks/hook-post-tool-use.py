#!/usr/bin/env python3
"""
Factory Droid Hook: PostToolUse (Enhanced v2)
Triggers after each tool (Edit, Create, Execute, Read, etc.) completes.

Features:
- Tool usage statistics
- Error capture and learning
- File modification tracking
- Context index updates
- Progress tracking

Input: JSON from stdin with tool_name, tool_input, tool_response
Output: Exit 0 for success, no blocking
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

def log_tool_usage(tool_name, tool_response):
    """Log tool usage for statistics."""
    try:
        stats_file = memory_dir / 'tool_stats.json'
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {'tools': {}, 'total_executions': 0, 'errors': 0}
        
        if tool_name not in stats['tools']:
            stats['tools'][tool_name] = {'count': 0, 'errors': 0}
        
        stats['tools'][tool_name]['count'] += 1
        stats['total_executions'] += 1
        stats['last_tool'] = tool_name
        stats['last_execution'] = datetime.now().isoformat()
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return True
    except:
        return False

def capture_error(tool_name, tool_input, tool_response):
    """Capture errors for learning."""
    # Check if response indicates an error
    error_indicators = [
        'error', 'Error', 'ERROR',
        'failed', 'Failed', 'FAILED',
        'exception', 'Exception',
        'not found', 'Not found',
        'permission denied', 'Permission denied',
        'syntax error', 'SyntaxError'
    ]
    
    response_str = str(tool_response) if tool_response else ''
    
    # Check for errors
    has_error = False
    error_type = None
    
    for indicator in error_indicators:
        if indicator in response_str:
            has_error = True
            error_type = indicator
            break
    
    if not has_error:
        return None
    
    # Extract error details
    error_info = {
        'tool': tool_name,
        'error_type': error_type,
        'timestamp': datetime.now().isoformat()
    }
    
    # Extract file path if available
    if isinstance(tool_input, dict):
        error_info['file_path'] = tool_input.get('file_path') or tool_input.get('path')
        error_info['command'] = tool_input.get('command')
    
    # Extract error message (first 500 chars)
    error_info['message'] = response_str[:500] if len(response_str) > 500 else response_str
    
    return error_info

def record_error_to_knowledge(error_info):
    """Record error to knowledge/mistakes for learning."""
    try:
        # Record to errors file
        errors_file = memory_dir / 'captured_errors.json'
        
        if errors_file.exists():
            with open(errors_file, 'r') as f:
                errors = json.load(f)
        else:
            errors = {'errors': [], 'patterns': {}}
        
        errors['errors'].append(error_info)
        
        # Track error patterns
        error_type = error_info.get('error_type', 'unknown')
        if error_type not in errors['patterns']:
            errors['patterns'][error_type] = 0
        errors['patterns'][error_type] += 1
        
        # Keep only last 100 errors
        if len(errors['errors']) > 100:
            errors['errors'] = errors['errors'][-100:]
        
        with open(errors_file, 'w') as f:
            json.dump(errors, f, indent=2)
        
        # Update tool stats with error count
        try:
            stats_file = memory_dir / 'tool_stats.json'
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                stats['errors'] = stats.get('errors', 0) + 1
                tool_name = error_info.get('tool', 'unknown')
                if tool_name in stats['tools']:
                    stats['tools'][tool_name]['errors'] = stats['tools'][tool_name].get('errors', 0) + 1
                with open(stats_file, 'w') as f:
                    json.dump(stats, f, indent=2)
        except:
            pass
        
        # Try to record via shared_context
        try:
            from shared_context import SharedContext
            sc = SharedContext()
            sc.record_error(
                error_info.get('message', 'Unknown error')[:200],
                agent=None,
                recoverable=True
            )
        except:
            pass
        
        return True
    except:
        return False

def track_file_modification(tool_name, tool_input, tool_response):
    """Track file modifications and update project tree."""
    if tool_name not in ['Edit', 'Create', 'Write', 'MultiEdit']:
        return
    
    try:
        file_path = None
        if isinstance(tool_input, dict):
            file_path = tool_input.get('file_path') or tool_input.get('path')
        
        if not file_path:
            return
        
        # Determine action
        action = 'modified' if tool_name == 'Edit' else 'created'
        
        # Update files_modified tracking
        files_file = memory_dir / 'files_modified.json'
        
        if files_file.exists():
            with open(files_file, 'r') as f:
                files = json.load(f)
        else:
            files = {}
        
        files[file_path] = {
            'modified_at': datetime.now().isoformat(),
            'by_tool': tool_name,
            'action': action
        }
        
        with open(files_file, 'w') as f:
            json.dump(files, f, indent=2)
        
        # Update context index AND project tree
        try:
            from context_index import ContextIndex
            ci = ContextIndex()
            ci.record_file_modified(file_path, tool_name)
            
            # Update project tree if this is a new file
            if action == 'created':
                current_project = ci.index.get('current_project')
                if current_project and file_path.startswith(current_project):
                    ci.update_project_tree(current_project, file_path, 'created')
        except:
            pass
        
        # Update shared context
        try:
            from shared_context import SharedContext
            sc = SharedContext()
            sc.record_file_change(file_path, action)
        except:
            pass
            
    except:
        pass

def track_file_deletion(tool_name, tool_input, tool_response):
    """Track file deletions and update project tree."""
    # Check if this was a delete operation
    if tool_name != 'Execute':
        return
    
    try:
        command = ''
        if isinstance(tool_input, dict):
            command = tool_input.get('command', '')
        
        # Check for delete commands
        delete_patterns = ['rm ', 'del ', 'Remove-Item', 'unlink']
        is_delete = any(p in command for p in delete_patterns)
        
        if not is_delete:
            return
        
        # Try to extract file path from command
        # This is best-effort
        response_str = str(tool_response) if tool_response else ''
        if 'error' not in response_str.lower():
            # Update project tree
            try:
                from context_index import ContextIndex
                ci = ContextIndex()
                current_project = ci.index.get('current_project')
                if current_project:
                    # Note: We can't easily extract the exact file, but we can
                    # flag that a deletion occurred for re-indexing
                    ci.index['needs_reindex'] = True
                    ci._save_index()
            except:
                pass
    except:
        pass

def update_session_progress():
    """Update session progress."""
    try:
        session_file = memory_dir / 'session_state.json'
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                state = json.load(f)
        else:
            state = {'tools_used': 0}
        
        state['tools_used'] = state.get('tools_used', 0) + 1
        state['last_update'] = datetime.now().isoformat()
        
        # Backup memory every 10 tools
        if state['tools_used'] % 10 == 0:
            state['last_backup'] = datetime.now().isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    except:
        pass

def main():
    try:
        # Read input from Droid (Factory AI PostToolUse format)
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get('tool_name', 'unknown')
        tool_input = input_data.get('tool_input', {})
        tool_response = input_data.get('tool_response', {})
        
        # Log tool usage
        log_tool_usage(tool_name, tool_response)
        
        # Capture errors
        error_info = capture_error(tool_name, tool_input, tool_response)
        if error_info:
            record_error_to_knowledge(error_info)
        
        # Track file modifications
        track_file_modification(tool_name, tool_input, tool_response)
        
        # Track file deletions (updates project tree)
        track_file_deletion(tool_name, tool_input, tool_response)
        
        # Update progress
        update_session_progress()
        
        # Exit 0 = success, no blocking
        sys.exit(0)
        
    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        sys.exit(0)

if __name__ == '__main__':
    main()
