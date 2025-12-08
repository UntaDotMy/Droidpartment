#!/usr/bin/env python3
"""
Factory Droid Hook: SessionStart (Enhanced v2)
Triggers when Droid starts a new session or resumes existing session.

Features:
- Environment discovery (cached 24 hours)
- Memory initialization
- Context injection for all agents
- Workflow state initialization
- Shared context setup

Input: JSON from stdin with session metadata
Output: JSON with additionalContext for Droid
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add memory directory to path for imports
memory_dir = Path(os.path.expanduser('~/.factory/memory'))
sys.path.insert(0, str(memory_dir))

def discover_environment():
    """Discover environment using context_index module."""
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        return ci.discover_environment()
    except ImportError:
        # Fallback if module not available
        return discover_environment_fallback()
    except Exception as e:
        return {'error': str(e)}

def discover_environment_fallback():
    """Fallback environment discovery without module."""
    import platform
    import subprocess
    
    def check_tool(name):
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(f'where {name}', shell=True, capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(f'which {name}', shell=True, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    tools = ['git', 'node', 'npm', 'python', 'docker']
    available = [t for t in tools if check_tool(t)]
    
    return {
        'os': {'system': platform.system(), 'release': platform.release()},
        'shell': {'name': 'PowerShell' if platform.system() == 'Windows' else 'bash'},
        'tools': {t: {'available': t in available} for t in tools}
    }

def initialize_workflow_state():
    """Initialize workflow state for session."""
    try:
        from workflow_state import WorkflowState
        ws = WorkflowState()
        ws.reset()  # Fresh state for new session
        return ws.get_summary()
    except ImportError:
        return '[Workflow state not available]'
    except Exception as e:
        return f'[Workflow error: {e}]'

def initialize_shared_context(session_id):
    """Initialize shared context for session."""
    try:
        from shared_context import SharedContext
        sc = SharedContext()
        sc.reset()  # Fresh context for new session
        sc.set_session(session_id)
        return True
    except ImportError:
        return False
    except Exception as e:
        return False

def load_memory():
    """Load memory statistics."""
    try:
        lessons_file = memory_dir / 'lessons.yaml'
        patterns_file = memory_dir / 'patterns.yaml'
        mistakes_file = memory_dir / 'mistakes.yaml'
        
        def count_entries(filepath):
            try:
                content = filepath.read_text()
                return content.count('- id:')
            except:
                return 0
        
        return {
            'lessons': count_entries(lessons_file),
            'patterns': count_entries(patterns_file),
            'mistakes': count_entries(mistakes_file)
        }
    except:
        return {'lessons': 0, 'patterns': 0, 'mistakes': 0}

def create_session_state():
    """Create session state file."""
    try:
        session_state = {
            'status': 'active',
            'tools_used': 0,
            'agents_run': [],
            'droid_stats': {},
            'memory_loaded': True,
            'started_at': datetime.now().isoformat()
        }
        
        session_file = memory_dir / 'session_state.json'
        with open(session_file, 'w') as f:
            json.dump(session_state, f, indent=2)
        return True
    except:
        return False

def index_project_if_needed(cwd):
    """Index project if not already indexed (runs once per project)."""
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        
        # Check if project needs indexing
        if not ci.is_project_indexed(cwd):
            # First time for this project - index it
            project_index = ci.index_project(cwd)
            return project_index
        else:
            # Already indexed - load existing
            return ci.load_project_index(cwd)
    except ImportError:
        return None
    except Exception as e:
        return None

def build_context_injection(env, memory, workflow_summary, project_index, cwd):
    """Build context string to inject into Droid."""
    parts = []
    
    # Environment summary
    if env and not env.get('error'):
        os_info = env.get('os', {})
        shell = env.get('shell', {})
        os_str = f"{os_info.get('system', 'unknown')} {os_info.get('release', '')}".strip()
        shell_str = shell.get('name', 'unknown')
        shell_type = shell.get('type', 'unknown')
        parts.append(f"[Env: {os_str} | Shell: {shell_str} ({shell_type})]")
        
        # Tools
        tools = env.get('tools', {})
        available = [t for t, info in tools.items() if info.get('available')]
        if available:
            parts.append(f"[Tools: {', '.join(available[:8])}]")
    
    # Memory summary
    if memory:
        parts.append(f"[Memory: {memory.get('lessons', 0)} lessons, {memory.get('patterns', 0)} patterns, {memory.get('mistakes', 0)} mistakes]")
    
    # Project summary (if indexed)
    if project_index:
        proj_name = project_index.get('name', Path(cwd).name)
        proj_type = project_index.get('type', 'unknown')
        file_count = project_index.get('stats', {}).get('total_files', 0)
        framework = project_index.get('framework')
        
        proj_str = f"[Project: {proj_name} ({proj_type})"
        if framework:
            proj_str += f" | {framework}"
        proj_str += f" | {file_count} files]"
        parts.append(proj_str)
        
        # Key directories
        code_dirs = project_index.get('relationships', {}).get('directories_with_code', [])[:3]
        if code_dirs:
            parts.append(f"[Code in: {', '.join(code_dirs)}]")
    
    # Workflow state
    if workflow_summary and '[' in workflow_summary:
        parts.append(workflow_summary)
    
    return ' '.join(parts) if parts else ''

def main():
    try:
        # Read input from Droid (Factory AI format)
        input_data = json.load(sys.stdin)
        session_id = input_data.get('session_id', 'unknown')
        source = input_data.get('source', 'startup')
        cwd = input_data.get('cwd', os.getcwd())
        
        # Initialize systems
        env = discover_environment()
        memory = load_memory()
        workflow_summary = initialize_workflow_state()
        initialize_shared_context(session_id)
        create_session_state()
        
        # Index project (runs once per project, cached)
        project_index = index_project_if_needed(cwd)
        
        # Build context to inject
        additional_context = build_context_injection(env, memory, workflow_summary, project_index, cwd)
        
        # Add Droidpartment banner
        if additional_context:
            additional_context = f"[Droidpartment v3.2.0] {additional_context}"
        
        # Factory AI JSON output format for SessionStart
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
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
