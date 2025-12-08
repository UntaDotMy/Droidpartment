#!/usr/bin/env python3
"""
Memory System - Three-layer learning for agents

Provides persistent learning across sessions:
- Global: Lessons, patterns, mistakes (all projects)
- Session: Data for current task
- Per-project: Project-specific knowledge

Version: 3.2.0
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str
    type: str  # "lesson", "pattern", "mistake"
    content: str
    agent: str
    project: Optional[str]
    timestamp: str
    confidence: int

class ThreeLayerMemory:
    """Three-layer memory system for agents"""
    
    def __init__(self, memory_dir: Optional[str] = None):
        """Initialize memory system"""
        self.memory_dir = Path(memory_dir or os.path.expanduser("~/.factory/memory"))
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Layer 1: Global memory (shared)
        self.global_dir = self.memory_dir
        
        # Layer 2: Session memory (current task)
        self.session_data: Dict[str, Dict[str, Any]] = {}
        
        # Layer 3: Project memory
        self.project_dir = self.memory_dir / "projects"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_global_memory()
    
    def _load_global_memory(self) -> None:
        """Load global memory files"""
        self.lessons = self._load_yaml(self.global_dir / "lessons.yaml")
        self.patterns = self._load_yaml(self.global_dir / "patterns.yaml")
        self.mistakes = self._load_yaml(self.global_dir / "mistakes.yaml")
    
    def _load_yaml(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load YAML-like memory file"""
        if not filepath.exists():
            return []
        
        try:
            with open(filepath) as f:
                content = f.read()
                # Simple YAML parsing for memory files
                entries = []
                for line in content.split('\n'):
                    if line.strip().startswith('- '):
                        # This is simplified - real YAML parsing would be more complex
                        pass
                return entries
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")
            return []
    
    def register_agent_activity(self, agent: str, activity: str) -> None:
        """Register that an agent started an activity"""
        self.session_data[agent] = {
            "activity": activity,
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
    
    def store_in_session(
        self,
        agent: str,
        key: str,
        data: Dict[str, Any]
    ) -> str:
        """Store data in current session for other agents"""
        session_id = f"session_{agent}_{key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if agent not in self.session_data:
            self.session_data[agent] = {}
        
        self.session_data[agent][key] = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        return session_id
    
    def get_from_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve data stored in session"""
        for agent_data in self.session_data.values():
            for key, entry in agent_data.items():
                if isinstance(entry, dict) and entry.get("session_id") == session_id:
                    return entry.get("data")
        return None
    
    def learn_pattern(
        self,
        agent: str,
        project: Optional[str],
        pattern_type: str,
        pattern: str,
        confidence: int = 80
    ) -> None:
        """Learn a successful pattern"""
        entry = MemoryEntry(
            id=f"pattern_{agent}_{datetime.now().timestamp()}",
            type="pattern",
            content=pattern,
            agent=agent,
            project=project,
            timestamp=datetime.now().isoformat(),
            confidence=confidence
        )
        
        if not hasattr(self, 'patterns'):
            self.patterns = []
        
        self.patterns.append(asdict(entry))
        self._save_global_memory()
    
    def learn_mistake(
        self,
        agent: str,
        project: Optional[str],
        mistake: str,
        lesson: str,
        severity: str = "medium"
    ) -> None:
        """Learn from a mistake"""
        entry = MemoryEntry(
            id=f"mistake_{agent}_{datetime.now().timestamp()}",
            type="mistake",
            content=f"{mistake} → {lesson}",
            agent=agent,
            project=project,
            timestamp=datetime.now().isoformat(),
            confidence=90
        )
        
        if not hasattr(self, 'mistakes'):
            self.mistakes = []
        
        self.mistakes.append(asdict(entry))
        self._save_global_memory()
    
    def store_project_knowledge(
        self,
        project: str,
        knowledge_type: str,
        content: Dict[str, Any]
    ) -> None:
        """Store project-specific knowledge"""
        project_dir = self.project_dir / project
        project_dir.mkdir(parents=True, exist_ok=True)
        
        knowledge_file = project_dir / f"{knowledge_type}.json"
        
        with open(knowledge_file, 'w') as f:
            json.dump(content, f, indent=2)
    
    def get_project_knowledge(
        self,
        project: str,
        knowledge_type: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve project knowledge"""
        knowledge_file = self.project_dir / project / f"{knowledge_type}.json"
        
        if not knowledge_file.exists():
            return None
        
        try:
            with open(knowledge_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load project knowledge: {e}")
            return None
    
    def _save_global_memory(self) -> None:
        """Save global memory to files"""
        # Convert to YAML-like format
        if hasattr(self, 'patterns'):
            self._save_yaml(self.global_dir / "patterns.yaml", self.patterns)
        
        if hasattr(self, 'mistakes'):
            self._save_yaml(self.global_dir / "mistakes.yaml", self.mistakes)
    
    def _save_yaml(self, filepath: Path, entries: List[Dict[str, Any]]) -> None:
        """Save entries as YAML-like file"""
        try:
            with open(filepath, 'w') as f:
                f.write("# Memory entries\n")
                for entry in entries:
                    f.write(f"- id: {entry.get('id')}\n")
                    f.write(f"  type: {entry.get('type')}\n")
                    f.write(f"  content: {entry.get('content')}\n")
        except Exception as e:
            print(f"Warning: Failed to save {filepath}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "lessons_count": len(self.lessons) if hasattr(self, 'lessons') else 0,
            "patterns_count": len(self.patterns) if hasattr(self, 'patterns') else 0,
            "mistakes_count": len(self.mistakes) if hasattr(self, 'mistakes') else 0,
            "timestamp": datetime.now().isoformat()
        }

# Module-level instance
_memory = None

def get_memory_system() -> ThreeLayerMemory:
    """Get global memory system instance"""
    global _memory
    if _memory is None:
        _memory = ThreeLayerMemory()
    return _memory

def store_in_session(agent: str, key: str, data: Dict[str, Any]) -> str:
    """Store in current session"""
    memory = get_memory_system()
    return memory.store_in_session(agent, key, data)

def get_from_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get from session"""
    memory = get_memory_system()
    return memory.get_from_session(session_id)

def track_agent_efficiency(agent: str, operation: str, tokens: int) -> None:
    """Track agent efficiency metrics"""
    memory = get_memory_system()
    memory.store_in_session(
        agent,
        "efficiency",
        {
            "operation": operation,
            "tokens": tokens,
            "timestamp": datetime.now().isoformat()
        }
    )

# Expose three_layer_memory for compatibility
three_layer_memory = None

def _init_three_layer_memory():
    global three_layer_memory
    if three_layer_memory is None:
        three_layer_memory = get_memory_system()

_init_three_layer_memory()

if __name__ == "__main__":
    # Test memory system
    memory = get_memory_system()
    print("Statistics:", json.dumps(memory.get_statistics(), indent=2))
