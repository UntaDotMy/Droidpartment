#!/usr/bin/env python3
"""
Workflow State Machine for Droidpartment
Tracks workflow phases, enables loops, and manages state transitions.

States:
- init: Session starting, environment discovery
- discovery: Analyzing codebase, gathering context
- planning: Breaking down tasks, creating plan
- execution: Implementing tasks
- review: Quality checks, testing
- iteration: Brainstorm loop, refining work
- complete: Task finished

Pure Python stdlib - no external dependencies.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# State definitions
STATES = ['init', 'discovery', 'planning', 'execution', 'review', 'iteration', 'complete']

# Valid state transitions
TRANSITIONS = {
    'init': ['discovery', 'planning', 'complete'],
    'discovery': ['planning', 'execution', 'complete'],
    'planning': ['execution', 'discovery', 'complete'],
    'execution': ['review', 'iteration', 'complete'],
    'review': ['execution', 'iteration', 'complete'],
    'iteration': ['planning', 'execution', 'review', 'complete'],
    'complete': []  # Terminal state
}

# Agent to state mapping (which agents typically run in which state)
AGENT_STATES = {
    'dpt-init': 'init',
    'dpt-memory': 'init',
    'dpt-research': 'discovery',
    'dpt-product': 'planning',
    'dpt-scrum': 'planning',
    'dpt-arch': 'planning',
    'dpt-dev': 'execution',
    'dpt-data': 'execution',
    'dpt-api': 'execution',
    'dpt-ux': 'execution',
    'dpt-ops': 'execution',
    'dpt-qa': 'review',
    'dpt-sec': 'review',
    'dpt-lead': 'review',
    'dpt-perf': 'review',
    'dpt-review': 'review',
    'dpt-docs': 'complete',
    'dpt-grammar': 'complete',
    'dpt-output': 'complete'
}

class WorkflowState:
    """Manages workflow state for a session."""
    
    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or Path(os.path.expanduser('~/.factory/memory'))
        self.state_file = self.memory_dir / 'workflow_state.json'
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load state from file or create default."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self._default_state()
    
    def _default_state(self) -> Dict:
        """Create default state."""
        return {
            'current_state': 'init',
            'previous_state': None,
            'iteration_count': 0,
            'max_iterations': 5,
            'state_history': [],
            'agent_outputs': {},
            'pending_handoffs': [],
            'errors_captured': [],
            'last_agent': None,
            'next_agent_hint': None,
            'brainstorm_active': False,
            'brainstorm_topic': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Save state to file."""
        self.state['updated_at'] = datetime.now().isoformat()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_state(self) -> str:
        """Get current state."""
        return self.state['current_state']
    
    def can_transition(self, new_state: str) -> bool:
        """Check if transition is valid."""
        current = self.state['current_state']
        return new_state in TRANSITIONS.get(current, [])
    
    def transition(self, new_state: str, reason: str = '') -> bool:
        """Transition to new state if valid."""
        if not self.can_transition(new_state):
            return False
        
        # Record history
        self.state['state_history'].append({
            'from': self.state['current_state'],
            'to': new_state,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
        self.state['previous_state'] = self.state['current_state']
        self.state['current_state'] = new_state
        
        # Track iterations
        if new_state == 'iteration':
            self.state['iteration_count'] += 1
        
        self._save_state()
        return True
    
    def should_loop(self) -> bool:
        """Check if we should continue looping."""
        if not self.state['brainstorm_active']:
            return False
        if self.state['iteration_count'] >= self.state['max_iterations']:
            return False
        return True
    
    def start_brainstorm(self, topic: str):
        """Start a brainstorm/iteration loop."""
        self.state['brainstorm_active'] = True
        self.state['brainstorm_topic'] = topic
        self.state['iteration_count'] = 0
        self._save_state()
    
    def end_brainstorm(self):
        """End brainstorm loop."""
        self.state['brainstorm_active'] = False
        self.state['brainstorm_topic'] = None
        self._save_state()
    
    def record_agent_output(self, agent: str, output: Any):
        """Record output from an agent."""
        self.state['agent_outputs'][agent] = {
            'output': output,
            'timestamp': datetime.now().isoformat()
        }
        self.state['last_agent'] = agent
        self._save_state()
    
    def get_agent_output(self, agent: str) -> Optional[Any]:
        """Get output from a specific agent."""
        return self.state['agent_outputs'].get(agent, {}).get('output')
    
    def get_all_outputs(self) -> Dict:
        """Get all agent outputs."""
        return self.state['agent_outputs']
    
    def set_next_agent_hint(self, agent: str):
        """Hint which agent should run next."""
        self.state['next_agent_hint'] = agent
        self._save_state()
    
    def get_next_agent_hint(self) -> Optional[str]:
        """Get hint for next agent."""
        hint = self.state['next_agent_hint']
        self.state['next_agent_hint'] = None  # Clear after reading
        self._save_state()
        return hint
    
    def add_pending_handoff(self, from_agent: str, to_agent: str, context: Dict):
        """Add a pending handoff between agents."""
        self.state['pending_handoffs'].append({
            'from': from_agent,
            'to': to_agent,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        self._save_state()
    
    def get_pending_handoffs(self, for_agent: str) -> List[Dict]:
        """Get pending handoffs for an agent."""
        handoffs = [h for h in self.state['pending_handoffs'] if h['to'] == for_agent]
        # Clear retrieved handoffs
        self.state['pending_handoffs'] = [h for h in self.state['pending_handoffs'] if h['to'] != for_agent]
        self._save_state()
        return handoffs
    
    def capture_error(self, error: str, context: Dict = None):
        """Capture an error for learning."""
        self.state['errors_captured'].append({
            'error': error,
            'context': context or {},
            'state': self.state['current_state'],
            'timestamp': datetime.now().isoformat()
        })
        self._save_state()
    
    def get_errors(self) -> List[Dict]:
        """Get captured errors."""
        return self.state['errors_captured']
    
    def clear_errors(self):
        """Clear captured errors after processing."""
        self.state['errors_captured'] = []
        self._save_state()
    
    def get_summary(self) -> str:
        """Get human-readable state summary."""
        s = self.state
        summary = f"[Workflow State: {s['current_state']}]"
        
        if s['brainstorm_active']:
            summary += f" [Brainstorm: {s['brainstorm_topic']} - iteration {s['iteration_count']}/{s['max_iterations']}]"
        
        if s['last_agent']:
            summary += f" [Last: {s['last_agent']}]"
        
        if s['next_agent_hint']:
            summary += f" [Next: {s['next_agent_hint']}]"
        
        if s['errors_captured']:
            summary += f" [Errors: {len(s['errors_captured'])}]"
        
        return summary
    
    def reset(self):
        """Reset state for new session."""
        self.state = self._default_state()
        self._save_state()


# Convenience functions for hook scripts
def get_workflow_state() -> WorkflowState:
    """Get workflow state instance."""
    return WorkflowState()

def get_state_summary() -> str:
    """Get current state summary."""
    return WorkflowState().get_summary()

def should_continue_loop() -> bool:
    """Check if brainstorm loop should continue."""
    return WorkflowState().should_loop()

def infer_state_from_agent(agent: str) -> str:
    """Infer workflow state from agent name."""
    return AGENT_STATES.get(agent, 'execution')


if __name__ == '__main__':
    # Test
    ws = WorkflowState()
    print(f"Current state: {ws.get_state()}")
    print(f"Summary: {ws.get_summary()}")
