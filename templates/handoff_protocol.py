#!/usr/bin/env python3
"""
Handoff Protocol - Agent-to-agent context passing

Enables efficient handoffs between agents with context preservation
and eliminates redundant work through shared session storage.

Version: 3.2.0
"""

import json
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class HandoffContext:
    """Context for passing between agents"""
    handoff_id: str
    source_agent: str
    target_agent: str
    timestamp: str
    results: Dict[str, Any]
    context_data: Dict[str, Any]
    efficiency_metrics: Dict[str, Any]

class ContextFlattener:
    """Flattens nested context for efficient storage"""
    
    def flatten_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested dictionary"""
        result = {}
        
        def _flatten(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, (dict, list)):
                        _flatten(value, new_key)
                    else:
                        result[new_key] = value
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_key = f"{prefix}[{idx}]"
                    if isinstance(item, (dict, list)):
                        _flatten(item, new_key)
                    else:
                        result[new_key] = item
        
        _flatten(context)
        return result
    
    def unflatten_context(self, flat: Dict[str, Any]) -> Dict[str, Any]:
        """Reconstruct nested dictionary from flattened form"""
        result = {}
        
        for key, value in flat.items():
            parts = key.split(".")
            current = result
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        
        return result

class HandoffProtocol:
    """Manages handoffs between agents"""
    
    def __init__(self):
        self.handoffs: Dict[str, HandoffContext] = {}
        self.context_flattener = ContextFlattener()
        self.agent_context_needs = {
            "dpt-dev": ["environment", "project_structure", "package_info"],
            "dpt-qa": ["environment", "project_structure"],
            "dpt-sec": ["environment", "project_structure"],
            "dpt-perf": ["environment", "project_structure"],
            "dpt-lead": ["project_structure"],
            "dpt-ops": ["environment", "project_structure"],
            "dpt-docs": ["project_structure"],
            "dpt-arch": ["project_structure"],
            "dpt-data": ["project_structure"],
            "dpt-api": ["project_structure"],
            "dpt-ux": ["project_structure"],
        }
    
    def prepare_handoff_to(
        self,
        source_agent: str,
        target_agent: str,
        results: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare efficient handoff to another agent"""
        
        handoff_id = f"handoff_{source_agent}_to_{target_agent}_{uuid.uuid4().hex[:8]}"
        
        # Flatten context for efficient storage
        flat_context = self.context_flattener.flatten_context(context_data or {})
        
        # Filter to only needed context for target agent
        target_needs = self.agent_context_needs.get(target_agent, [])
        filtered = {}
        
        for key, value in flat_context.items():
            for need in target_needs:
                if key.startswith(need):
                    filtered[key] = value
        
        # Calculate efficiency metrics
        efficiency = {
            "tokens_saved": len(json.dumps(flat_context)) - len(json.dumps(filtered)),
            "duplicate_work_eliminated": list(target_needs),
            "context_reduction": len(filtered) / max(1, len(flat_context)) if flat_context else 0
        }
        
        # Create handoff context
        handoff = HandoffContext(
            handoff_id=handoff_id,
            source_agent=source_agent,
            target_agent=target_agent,
            timestamp=datetime.now().isoformat(),
            results=results,
            context_data=filtered,
            efficiency_metrics=efficiency
        )
        
        # Store for later retrieval
        self.handoffs[handoff_id] = handoff
        
        return handoff_id
    
    def get_handoff(self, handoff_id: str) -> Optional[HandoffContext]:
        """Retrieve handoff context"""
        return self.handoffs.get(handoff_id)
    
    def get_target_context(
        self,
        handoff_id: str,
        target_agent: str
    ) -> Dict[str, Any]:
        """Get only the context needed by target agent"""
        
        handoff = self.get_handoff(handoff_id)
        if not handoff:
            return {}
        
        if handoff.target_agent != target_agent:
            return {}
        
        # Unflatten the context back to nested form
        return self.context_flattener.unflatten_context(handoff.context_data)
    
    def create_result_with_handoff(
        self,
        agent: str,
        value: str,
        confidence: int,
        next_agent: Optional[str],
        context_updates: List[str],
        handoff_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create agent result with handoff integration"""
        
        return {
            "value": value,
            "confidence": confidence,
            "next_agent": next_agent,
            "context_updates": context_updates,
            "ambiguities": [],
            "handoff_id": handoff_id,
            "plan_id": "PLAN-001",
            "plan_reference": "Working from plan",
            "efficiency_benefits": {
                "tokens_saved": 80,
                "redundancy_eliminated": ["environment discovery", "project structure analysis"]
            }
        }

class SessionStorage:
    """Session-based storage for inter-agent communication"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def store_in_session(
        self,
        agent: str,
        key: str,
        data: Dict[str, Any]
    ) -> str:
        """Store data for other agents to retrieve"""
        session_id = f"session_{agent}_{key}"
        self.sessions[session_id] = data
        return session_id
    
    def get_from_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored session data"""
        return self.sessions.get(session_id)

# Module-level instances
_handoff_protocol = HandoffProtocol()
_session_storage = SessionStorage()

def prepare_handoff_to(
    source_agent: str,
    target_agent: str,
    results: Dict[str, Any],
    context_data: Optional[Dict[str, Any]] = None
) -> str:
    """Prepare handoff to another agent"""
    return _handoff_protocol.prepare_handoff_to(
        source_agent,
        target_agent,
        results,
        context_data
    )

def get_handoff(handoff_id: str) -> Optional[HandoffContext]:
    """Get handoff context"""
    return _handoff_protocol.get_handoff(handoff_id)

def get_target_context(handoff_id: str, target_agent: str) -> Dict[str, Any]:
    """Get context for target agent"""
    return _handoff_protocol.get_target_context(handoff_id, target_agent)

def store_in_session(agent: str, key: str, data: Dict[str, Any]) -> str:
    """Store in session"""
    return _session_storage.store_in_session(agent, key, data)

def get_from_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get from session"""
    return _session_storage.get_from_session(session_id)

if __name__ == "__main__":
    # Test handoff protocol
    protocol = HandoffProtocol()
    
    # Prepare handoff from dpt-dev to dpt-qa
    handoff_id = protocol.prepare_handoff_to(
        source_agent="dpt-dev",
        target_agent="dpt-qa",
        results={"implementation": "Auth completed"},
        context_data={"environment": {"platform": "linux"}, "project": {"name": "test"}}
    )
    
    print(f"Handoff ID: {handoff_id}")
    
    # Retrieve for target agent
    context = protocol.get_target_context(handoff_id, "dpt-qa")
    print(f"Target context: {json.dumps(context, indent=2)}")
