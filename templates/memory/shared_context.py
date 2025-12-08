#!/usr/bin/env python3
"""
Shared Context Manager for Droidpartment
Manages shared context between agents for seamless handoffs and collaboration.

Features:
- Agent output storage and retrieval
- Handoff context passing
- Iteration/loop tracking
- State synchronization
- All stored in ~/.factory/memory/shared_context.json

Pure Python stdlib - no external dependencies.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class SharedContext:
    """Manages shared context between agents."""
    
    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or Path(os.path.expanduser('~/.factory/memory'))
        self.context_file = self.memory_dir / 'shared_context.json'
        self.context = self._load_context()
    
    def _load_context(self) -> Dict:
        """Load context from file or create default."""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self._default_context()
    
    def _default_context(self) -> Dict:
        """Create default context structure."""
        return {
            'session': {
                'id': None,
                'started_at': datetime.now().isoformat(),
                'task_description': None,
                'user_intent': None
            },
            'workflow': {
                'current_phase': 'init',
                'iteration': 0,
                'max_iterations': 5,
                'loop_active': False,
                'loop_reason': None
            },
            'agents': {
                'last_agent': None,
                'next_agent': None,
                'outputs': {},
                'handoffs': []
            },
            'knowledge': {
                'discoveries': [],
                'decisions': [],
                'blockers': [],
                'questions': []
            },
            'files': {
                'created': [],
                'modified': [],
                'deleted': []
            },
            'errors': [],
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        }
    
    def _save_context(self):
        """Save context to file."""
        self.context['metadata']['updated_at'] = datetime.now().isoformat()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2)
    
    # Session management
    def set_session(self, session_id: str, task: str = None, intent: str = None):
        """Set session information."""
        self.context['session']['id'] = session_id
        self.context['session']['task_description'] = task
        self.context['session']['user_intent'] = intent
        self._save_context()
    
    def get_session(self) -> Dict:
        """Get session information."""
        return self.context['session']
    
    # Workflow management
    def set_phase(self, phase: str):
        """Set current workflow phase."""
        self.context['workflow']['current_phase'] = phase
        self._save_context()
    
    def get_phase(self) -> str:
        """Get current workflow phase."""
        return self.context['workflow']['current_phase']
    
    def start_loop(self, reason: str):
        """Start an iteration loop."""
        self.context['workflow']['loop_active'] = True
        self.context['workflow']['loop_reason'] = reason
        self.context['workflow']['iteration'] = 0
        self._save_context()
    
    def increment_iteration(self) -> int:
        """Increment iteration counter."""
        self.context['workflow']['iteration'] += 1
        self._save_context()
        return self.context['workflow']['iteration']
    
    def should_continue_loop(self) -> bool:
        """Check if loop should continue."""
        if not self.context['workflow']['loop_active']:
            return False
        return self.context['workflow']['iteration'] < self.context['workflow']['max_iterations']
    
    def end_loop(self):
        """End iteration loop."""
        self.context['workflow']['loop_active'] = False
        self.context['workflow']['loop_reason'] = None
        self._save_context()
    
    # Agent management
    def record_agent_output(self, agent: str, output: Any, next_agent: str = None):
        """Record output from an agent."""
        self.context['agents']['outputs'][agent] = {
            'output': output if isinstance(output, (str, dict, list)) else str(output),
            'timestamp': datetime.now().isoformat()
        }
        self.context['agents']['last_agent'] = agent
        if next_agent:
            self.context['agents']['next_agent'] = next_agent
        self._save_context()
    
    def get_agent_output(self, agent: str) -> Optional[Any]:
        """Get output from a specific agent."""
        return self.context['agents']['outputs'].get(agent, {}).get('output')
    
    def get_last_agent(self) -> Optional[str]:
        """Get last agent that ran."""
        return self.context['agents']['last_agent']
    
    def get_next_agent(self) -> Optional[str]:
        """Get suggested next agent."""
        next_agent = self.context['agents']['next_agent']
        self.context['agents']['next_agent'] = None  # Clear after reading
        self._save_context()
        return next_agent
    
    def add_handoff(self, from_agent: str, to_agent: str, context: Dict, priority: str = 'normal'):
        """Add a handoff between agents."""
        self.context['agents']['handoffs'].append({
            'from': from_agent,
            'to': to_agent,
            'context': context,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'consumed': False
        })
        self._save_context()
    
    def get_handoffs_for(self, agent: str) -> List[Dict]:
        """Get pending handoffs for an agent."""
        handoffs = []
        for h in self.context['agents']['handoffs']:
            if h['to'] == agent and not h['consumed']:
                h['consumed'] = True
                handoffs.append(h)
        self._save_context()
        return handoffs
    
    # Knowledge management
    def add_discovery(self, item: str, category: str = 'general'):
        """Add a discovery."""
        self.context['knowledge']['discoveries'].append({
            'item': item,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
        self._save_context()
    
    def add_decision(self, decision: str, reason: str = None):
        """Add a decision made."""
        self.context['knowledge']['decisions'].append({
            'decision': decision,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        self._save_context()
    
    def add_blocker(self, blocker: str, severity: str = 'medium'):
        """Add a blocker."""
        self.context['knowledge']['blockers'].append({
            'blocker': blocker,
            'severity': severity,
            'resolved': False,
            'timestamp': datetime.now().isoformat()
        })
        self._save_context()
    
    def add_question(self, question: str, for_user: bool = True):
        """Add a question that needs answering."""
        self.context['knowledge']['questions'].append({
            'question': question,
            'for_user': for_user,
            'answered': False,
            'timestamp': datetime.now().isoformat()
        })
        self._save_context()
    
    # File tracking
    def record_file_change(self, file_path: str, action: str):
        """Record a file change (created/modified/deleted)."""
        if action == 'created':
            if file_path not in self.context['files']['created']:
                self.context['files']['created'].append(file_path)
        elif action == 'modified':
            if file_path not in self.context['files']['modified']:
                self.context['files']['modified'].append(file_path)
        elif action == 'deleted':
            if file_path not in self.context['files']['deleted']:
                self.context['files']['deleted'].append(file_path)
        self._save_context()
    
    # Error tracking
    def record_error(self, error: str, agent: str = None, recoverable: bool = True):
        """Record an error."""
        self.context['errors'].append({
            'error': error,
            'agent': agent,
            'recoverable': recoverable,
            'timestamp': datetime.now().isoformat()
        })
        self._save_context()
    
    # Summary for injection
    def get_context_for_agent(self, agent: str) -> Dict:
        """Get context formatted for a specific agent."""
        return {
            'session': self.context['session'],
            'phase': self.context['workflow']['current_phase'],
            'iteration': self.context['workflow']['iteration'] if self.context['workflow']['loop_active'] else None,
            'last_agent': self.context['agents']['last_agent'],
            'last_output': self.get_agent_output(self.context['agents']['last_agent']) if self.context['agents']['last_agent'] else None,
            'handoffs': self.get_handoffs_for(agent),
            'discoveries': self.context['knowledge']['discoveries'][-5:],
            'blockers': [b for b in self.context['knowledge']['blockers'] if not b['resolved']],
            'recent_files': {
                'created': self.context['files']['created'][-5:],
                'modified': self.context['files']['modified'][-5:]
            },
            'errors': self.context['errors'][-3:]
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        parts = []
        
        # Phase
        parts.append(f"[Phase: {self.context['workflow']['current_phase']}]")
        
        # Loop status
        if self.context['workflow']['loop_active']:
            parts.append(f"[Loop: {self.context['workflow']['iteration']}/{self.context['workflow']['max_iterations']}]")
        
        # Last agent
        if self.context['agents']['last_agent']:
            parts.append(f"[Last: {self.context['agents']['last_agent']}]")
        
        # Pending handoffs
        pending = len([h for h in self.context['agents']['handoffs'] if not h['consumed']])
        if pending:
            parts.append(f"[Handoffs: {pending}]")
        
        # Blockers
        blockers = len([b for b in self.context['knowledge']['blockers'] if not b['resolved']])
        if blockers:
            parts.append(f"[Blockers: {blockers}]")
        
        # Errors
        if self.context['errors']:
            parts.append(f"[Errors: {len(self.context['errors'])}]")
        
        return ' '.join(parts)
    
    def reset(self):
        """Reset context for new session."""
        self.context = self._default_context()
        self._save_context()


# Convenience functions
def get_shared_context() -> SharedContext:
    """Get shared context instance."""
    return SharedContext()

def get_context_summary() -> str:
    """Get context summary."""
    return SharedContext().get_summary()


if __name__ == '__main__':
    # Test
    sc = SharedContext()
    sc.set_session('test123', task='Test task')
    sc.record_agent_output('dpt-dev', {'files_created': ['test.py']}, next_agent='dpt-qa')
    print(f"Summary: {sc.get_summary()}")
    print(f"Context for dpt-qa: {sc.get_context_for_agent('dpt-qa')}")
