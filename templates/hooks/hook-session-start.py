#!/usr/bin/env python3
"""
Factory Droid Hook: SessionStart (Enhanced v3)
Triggers when Droid starts a new session or resumes existing session.

Features:
- First-time project detection and initialization
- Project memory folder creation with STRUCTURE.md
- Environment discovery (cached 24 hours)
- Memory initialization with mistake warnings
- Context injection for all agents (file targeting without ls)
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

def initialize_project_memory(cwd):
    """
    Initialize project memory for first-time use.
    Creates project folder, indexes structure, saves STRUCTURE.md.
    Returns initialization info and project index.
    """
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        
        # Check if this is first time for this project
        is_first_time = not ci.is_project_indexed(cwd)
        
        # Initialize project memory (creates folder, STRUCTURE.md, files.json)
        init_result = ci.initialize_project_memory(cwd)
        
        # Load the project index
        project_index = ci.load_project_index(cwd)
        
        return {
            'is_first_time': is_first_time,
            'init_result': init_result,
            'project_index': project_index
        }
    except ImportError:
        return None
    except Exception as e:
        return None

def get_recent_mistakes(cwd, limit=3):
    """Get recent mistakes to warn agents."""
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        return ci.get_recent_mistakes(cwd, limit)
    except:
        return []


def check_resumable_session(cwd):
    """
    Check if there's a resumable session for the current project.
    Returns session info if found and has incomplete tasks.
    """
    try:
        sessions_dir = memory_dir / 'sessions'
        active_file = sessions_dir / 'active.json'
        
        if not active_file.exists():
            return None
        
        with open(active_file, 'r') as f:
            active = json.load(f)
        
        # Check if same project and has incomplete tasks
        if active.get('project') and cwd:
            # Normalize paths for comparison
            active_project = str(Path(active.get('project', '')).resolve())
            current_cwd = str(Path(cwd).resolve())
            
            if active_project == current_cwd and active.get('has_incomplete'):
                # Load full session data
                session_id = active.get('session_id')
                session_file = sessions_dir / f'{session_id}.json'
                
                if session_file.exists():
                    with open(session_file, 'r') as f:
                        return json.load(f)
        
        return None
    except:
        return None


def get_resume_context(resume_data):
    """Build context injection for resuming a session."""
    if not resume_data:
        return ""
    
    parts = ["[RESUMABLE SESSION DETECTED]"]
    
    state = resume_data.get('state', {})
    
    # Pending tasks
    pending = state.get('pending_tasks', [])
    if pending:
        parts.append(f"[Pending tasks from previous session: {len(pending)}]")
        for task in pending[:3]:
            parts.append(f"  - {task}")
    
    # Completed agents
    completed = state.get('completed_agents', [])
    if completed:
        parts.append(f"[Already completed: {', '.join(completed[-5:])}]")
    
    # Last saved time
    saved_at = resume_data.get('saved_at', '')
    if saved_at:
        parts.append(f"[Session saved: {saved_at}]")
    
    parts.append("[To continue previous work, ask to 'resume' or 'continue previous task']")
    
    return ' '.join(parts)

def get_project_files_summary(cwd):
    """Get file targeting info for agents (no ls needed)."""
    try:
        from context_index import ContextIndex
        ci = ContextIndex()
        project_index = ci.load_project_index(cwd)
        
        if not project_index:
            return None
        
        # Get key directories
        code_dirs = project_index.get('relationships', {}).get('directories_with_code', [])[:5]
        entry_points = project_index.get('relationships', {}).get('entry_points', [])[:3]
        config_files = project_index.get('key_files', {}).get('config', [])[:3]
        
        return {
            'code_dirs': code_dirs,
            'entry_points': entry_points,
            'config_files': config_files,
            'total_files': project_index.get('stats', {}).get('total_files', 0)
        }
    except:
        return None

def build_context_injection(env, memory, workflow_summary, project_init, cwd, mistakes):
    """Build context string to inject into Droid."""
    parts = []
    
    # First-time project indicator
    if project_init and project_init.get('is_first_time'):
        parts.append("[🆕 NEW PROJECT - Memory initialized, structure indexed]")
    
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
    project_index = project_init.get('project_index') if project_init else None
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
        
        # Key directories (agents can target without ls)
        code_dirs = project_index.get('relationships', {}).get('directories_with_code', [])[:5]
        if code_dirs:
            parts.append(f"[Code in: {', '.join(code_dirs)}]")
        
        # Entry points
        entry_points = project_index.get('relationships', {}).get('entry_points', [])[:3]
        if entry_points:
            parts.append(f"[Entry: {', '.join(entry_points)}]")
    
    # Recent mistakes to avoid
    if mistakes:
        mistake_strs = [f"⚠️ {m.get('mistake', 'unknown')[:50]}" for m in mistakes[:2]]
        parts.append(f"[Avoid: {'; '.join(mistake_strs)}]")
    
    # Workflow state
    if workflow_summary and '[' in workflow_summary:
        parts.append(workflow_summary)
    
    # Memory location for agents
    if project_init and project_init.get('init_result'):
        memory_dir = project_init['init_result'].get('memory_dir', '')
        if memory_dir:
            parts.append(f"[Project memory: {memory_dir}]")
    
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
        
        # Initialize project memory (first-time: creates folder, STRUCTURE.md, files.json)
        project_init = initialize_project_memory(cwd)
        
        # Get recent mistakes to warn agents
        mistakes = get_recent_mistakes(cwd, limit=3)
        
        # Check for resumable session (long workflow continuation)
        resume_data = check_resumable_session(cwd)
        resume_context = get_resume_context(resume_data) if resume_data else ""
        
        # Build context to inject
        additional_context = build_context_injection(
            env, memory, workflow_summary, project_init, cwd, mistakes
        )
        
        # Add resume context if available
        if resume_context:
            additional_context = f"{resume_context} {additional_context}"
        
        # Add Droidpartment INSTRUCTION (not just banner)
        version = "3.2.11"
        
        # Check if this is a NEW project (not yet in memory)
        is_new_project = project_init and project_init.get('is_first_time', False)
        
        # Get indexing feedback messages
        feedback_lines = ""
        if project_init and project_init.get('feedback'):
            feedback_lines = "\n".join(project_init['feedback'])
        
        # Get project ID for reference
        project_id = project_init.get('project_id', 'unknown') if project_init else 'unknown'
        memory_dir = project_init.get('memory_dir', '') if project_init else ''
        
        if is_new_project:
            # NEW PROJECT - must index first
            files_created = project_init.get('files_created', []) if project_init else []
            files_list = ", ".join([f for f in files_created if f])
            
            droidpartment_instruction = f"""
🤖 DROIDPARTMENT v{version} ACTIVE - NEW PROJECT DETECTED

═══════════════════════════════════════════════════════════════════════
📊 INDEXING COMPLETE - Project registered in memory
═══════════════════════════════════════════════════════════════════════
{feedback_lines}

📋 Project ID: {project_id}
📁 Memory folder: {memory_dir}
📄 Files created: {files_list}
═══════════════════════════════════════════════════════════════════════

✅ Project indexed! Now you can start working.

MANDATORY FIRST STEP (do this NOW):
Task(subagent_type: "dpt-memory", prompt: "START: {project_init.get('project_name', 'project')} - understand codebase, load context")

This will:
- Load the indexed structure into context
- Review existing patterns and lessons
- Prepare for the task

AFTER dpt-memory completes, the UserPromptSubmit hook will guide the specific workflow.

DO NOT skip this step. DO NOT call other agents before dpt-memory(START).
"""
        else:
            # EXISTING PROJECT - MANDATORY workflow
            droidpartment_instruction = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🤖 DROIDPARTMENT v{version} ACTIVE - MANDATORY AGENT USAGE                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  📋 Project: {project_id:<54} ║
║  📁 Memory: {memory_dir[-50:] if len(memory_dir) > 50 else memory_dir:<55} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  ⛔ FORBIDDEN ACTIONS:                                                       ║
║     • Writing code directly (use dpt-dev instead)                           ║
║     • Analyzing files directly (use dpt-arch or dpt-research)               ║
║     • Reviewing code directly (use dpt-lead or dpt-review)                  ║
║     • Testing directly (use dpt-qa)                                         ║
║     • ANY task without calling Task() first                                  ║
║                                                                              ║
║  ✅ REQUIRED ACTIONS:                                                        ║
║     • ALWAYS start with: Task(subagent_type: "dpt-memory", prompt: "START") ║
║     • ALWAYS delegate to appropriate dpt-* agent via Task()                 ║
║     • ALWAYS end with: Task(subagent_type: "dpt-memory", prompt: "END")     ║
║     • ALWAYS finish with: Task(subagent_type: "dpt-output", prompt: "...")  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

AVAILABLE AGENTS (call via Task tool):
• dpt-memory   - Learning (ALWAYS first and last)
• dpt-output   - Report synthesis (ALWAYS final)
• dpt-dev      - Code implementation
• dpt-qa       - Testing
• dpt-sec      - Security audit
• dpt-arch     - Architecture
• dpt-product  - Requirements/PRD
• dpt-scrum    - Task breakdown
• dpt-research - Best practices
• dpt-lead     - Code review
• dpt-review   - Simplicity check
• dpt-perf     - Performance
• dpt-data     - Database
• dpt-api      - API design
• dpt-ux       - UI/UX
• dpt-ops      - DevOps
• dpt-docs     - Documentation
• dpt-grammar  - Writing quality

Your job is ONLY to orchestrate Task() calls. The agents do the actual work.
The UserPromptSubmit hook will provide specific Task() calls for this request.
"""
        
        if additional_context:
            additional_context = f"{droidpartment_instruction}\n{additional_context}"
        else:
            additional_context = droidpartment_instruction
        
        # Build VISIBLE feedback message (systemMessage is shown to user!)
        if is_new_project:
            visible_message = f"""
🤖 DROIDPARTMENT v{version} - NEW PROJECT DETECTED
═══════════════════════════════════════════════════════════════════════
{feedback_lines}
📋 Project ID: {project_id}
📁 Memory: {memory_dir}
═══════════════════════════════════════════════════════════════════════
✅ Indexing complete! Starting memory agent...
"""
        else:
            file_count = project_init.get('file_count', 0) if project_init else 0
            visible_message = f"""
🤖 DROIDPARTMENT v{version} - PROJECT LOADED
═══════════════════════════════════════════════════════════════════════
📂 Project: {project_id}
📁 Memory: {memory_dir}
📊 Files indexed: {file_count}
═══════════════════════════════════════════════════════════════════════
"""
        
        # Factory AI JSON output format for SessionStart
        # - additionalContext: Goes to Droid's context (silent)
        # - systemMessage: VISIBLE to user in terminal!
        output = {
            "systemMessage": visible_message.strip(),
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
