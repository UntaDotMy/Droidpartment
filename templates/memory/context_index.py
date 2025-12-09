#!/usr/bin/env python3
"""
Context Indexer for Droidpartment (Enhanced v4)
Indexes project structure, caches context, provides shell-aware commands.

Features:
- First-time project detection and initialization
- Project memory folder creation with DETERMINISTIC naming
- Human-readable STRUCTURE.md generation
- Live incremental updates when files change
- File targeting without ls/find commands
- Shell-aware command suggestions
- Mistake tracking with prevention learning
- ML-inspired pattern recognition for agent selection

Pure Python stdlib - no external dependencies.

═══════════════════════════════════════════════════════════════════════════════
DATA ORGANIZATION: GLOBAL vs PROJECT-SPECIFIC
═══════════════════════════════════════════════════════════════════════════════

GLOBAL DATA (shared across all projects):
  ~/.factory/memory/
  ├── context_index.json      # Environment, shell, global state
  ├── project_registry.json   # Maps project paths to memory folders
  ├── global_mistakes.yaml    # High-severity mistakes (cross-project learning)
  ├── recognition_history.json # Pattern recognition learning history
  └── session_state.json      # Current session state

PROJECT-SPECIFIC DATA (isolated per project):
  ~/.factory/memory/projects/{project_name}_{hash}/
  ├── project_index.json      # Project structure index
  ├── STRUCTURE.md            # Human-readable structure
  ├── files.json              # Quick file lookup
  ├── lessons.yaml            # Project-specific lessons
  ├── mistakes.yaml           # Project-specific mistakes
  ├── patterns.yaml           # Project-specific patterns
  └── artifacts/              # Agent outputs (PRD.md, ARCHITECTURE.md, etc.)
      ├── PRD.md              # From dpt-product
      ├── ARCHITECTURE.md     # From dpt-arch
      ├── STORIES.md          # From dpt-scrum
      └── ...

Project naming uses MD5 hash for DETERMINISTIC consistency across sessions.
Example: "MyProject_a1b2c3d4" - always same hash for same path.
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import os
import sys
import re
import subprocess
import platform
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class ContextIndex:
    """Indexes and caches context for efficient agent access."""
    
    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or Path(os.path.expanduser('~/.factory/memory'))
        self.index_file = self.memory_dir / 'context_index.json'
        self.projects_dir = self.memory_dir / 'projects'
        self.registry_file = self.memory_dir / 'project_registry.json'  # NEW: Central registry
        self.index = self._load_index()
        self.registry = self._load_registry()
    
    # ==================== PROJECT REGISTRY (DETERMINISTIC) ====================
    
    def _load_registry(self) -> Dict:
        """Load project registry - maps project paths to their memory folder names."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'projects': {}, 'created_at': datetime.now().isoformat()}
    
    def _save_registry(self):
        """Save project registry."""
        self.registry['updated_at'] = datetime.now().isoformat()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def _get_deterministic_project_id(self, project_path: str) -> str:
        """
        Generate a DETERMINISTIC project ID that is consistent across sessions.
        Uses MD5 hash of the absolute path (NOT Python's hash() which is randomized).
        """
        abs_path = str(Path(project_path).resolve())
        # Use MD5 for deterministic hash (not for security, just for consistency)
        hash_digest = hashlib.md5(abs_path.encode()).hexdigest()[:8]
        project_name = Path(project_path).name
        return f"{project_name}_{hash_digest}"
    
    def get_project_memory_dir(self, project_path: str) -> Path:
        """
        Get the memory directory for a project.
        Uses registry to ensure SAME folder is used across sessions.
        """
        abs_path = str(Path(project_path).resolve())
        
        # Check registry first
        if abs_path in self.registry.get('projects', {}):
            return Path(self.registry['projects'][abs_path]['memory_dir'])
        
        # Create new entry with deterministic ID
        project_id = self._get_deterministic_project_id(project_path)
        memory_dir = self.projects_dir / project_id
        
        # Register it
        self.registry['projects'][abs_path] = {
            'project_id': project_id,
            'project_name': Path(project_path).name,
            'memory_dir': str(memory_dir),
            'registered_at': datetime.now().isoformat()
        }
        self._save_registry()
        
        return memory_dir
    
    def lookup_project(self, project_name_or_path: str) -> Optional[Dict]:
        """
        Lookup a project by name or path.
        Returns project info from registry.
        """
        # Try exact path match first
        if project_name_or_path in self.registry.get('projects', {}):
            return self.registry['projects'][project_name_or_path]
        
        # Try by project name
        for path, info in self.registry.get('projects', {}).items():
            if info.get('project_name') == project_name_or_path:
                return info
            if info.get('project_id') == project_name_or_path:
                return info
        
        return None
    
    def _load_index(self) -> Dict:
        """Load index from file or create default."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self._default_index()
    
    def _default_index(self) -> Dict:
        """Create default index structure."""
        return {
            'environment': {},
            'shell': {},
            'command_mappings': {},  # Shell-specific commands
            'command_errors': [],     # Learn from command failures
            'projects_indexed': {},   # Track which projects have been indexed
            'current_project': None,
            'files_read': {},
            'files_modified': {},
            'agent_summaries': {},
            'errors': [],
            'discoveries': [],
            'cache_valid_until': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def _save_index(self):
        """Save index to file."""
        self.index['updated_at'] = datetime.now().isoformat()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _run_command(self, cmd: str, shell: bool = True) -> Optional[str]:
        """Run a command and return output."""
        try:
            result = subprocess.run(
                cmd, shell=shell, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except:
            return None
    
    def _check_tool(self, name: str) -> Dict:
        """Check if a tool is available."""
        if platform.system() == 'Windows':
            which_cmd = f'where {name}'
        else:
            which_cmd = f'which {name}'
        
        path = self._run_command(which_cmd)
        if path:
            version = self._run_command(f'{name} --version') or 'unknown'
            return {'available': True, 'path': path.split('\n')[0], 'version': version.split('\n')[0]}
        return {'available': False, 'path': None, 'version': None}
    
    # ==================== SHELL DETECTION & COMMANDS ====================
    
    def detect_shell(self) -> Dict:
        """Detect current shell and store command mappings."""
        shell_info = {
            'type': 'unknown',
            'name': 'unknown',
            'version': 'unknown',
            'path': None
        }
        
        if platform.system() == 'Windows':
            # Check PowerShell first
            ps_version = self._run_command('$PSVersionTable.PSVersion.ToString()')
            if ps_version:
                shell_info['type'] = 'powershell'
                shell_info['name'] = 'PowerShell'
                shell_info['version'] = ps_version
                shell_info['path'] = self._run_command('(Get-Command powershell).Source') or 'powershell'
            else:
                shell_info['type'] = 'cmd'
                shell_info['name'] = 'cmd.exe'
                shell_info['path'] = os.getenv('COMSPEC', 'cmd.exe')
        else:
            shell_path = os.getenv('SHELL', '/bin/sh')
            shell_info['path'] = shell_path
            shell_name = Path(shell_path).name
            shell_info['name'] = shell_name
            
            if 'bash' in shell_name:
                shell_info['type'] = 'bash'
                shell_info['version'] = self._run_command('bash --version') or 'unknown'
            elif 'zsh' in shell_name:
                shell_info['type'] = 'zsh'
                shell_info['version'] = self._run_command('zsh --version') or 'unknown'
            else:
                shell_info['type'] = 'sh'
        
        # Store command mappings for this shell
        self.index['shell'] = shell_info
        self.index['command_mappings'] = self._get_command_mappings(shell_info['type'])
        self._save_index()
        
        return shell_info
    
    def _get_command_mappings(self, shell_type: str) -> Dict:
        """Get shell-specific command mappings."""
        if shell_type == 'powershell':
            return {
                'list_files': 'Get-ChildItem',
                'list_files_recursive': 'Get-ChildItem -Recurse',
                'find_file': 'Get-ChildItem -Recurse -Filter',
                'read_file': 'Get-Content',
                'create_dir': 'New-Item -ItemType Directory -Path',
                'remove_file': 'Remove-Item',
                'remove_dir': 'Remove-Item -Recurse -Force',
                'copy_file': 'Copy-Item',
                'move_file': 'Move-Item',
                'current_dir': 'Get-Location',
                'change_dir': 'Set-Location',
                'env_var': '$env:',
                'path_separator': '\\',
                'command_separator': ';',
                'pipe': '|',
                'grep': 'Select-String',
                'cat': 'Get-Content',
                'echo': 'Write-Output',
                'null_redirect': '| Out-Null',
                'error_redirect': '2>&1',
            }
        elif shell_type in ['bash', 'zsh', 'sh']:
            return {
                'list_files': 'ls',
                'list_files_recursive': 'ls -R',
                'find_file': 'find . -name',
                'read_file': 'cat',
                'create_dir': 'mkdir -p',
                'remove_file': 'rm',
                'remove_dir': 'rm -rf',
                'copy_file': 'cp',
                'move_file': 'mv',
                'current_dir': 'pwd',
                'change_dir': 'cd',
                'env_var': '$',
                'path_separator': '/',
                'command_separator': '&&',
                'pipe': '|',
                'grep': 'grep',
                'cat': 'cat',
                'echo': 'echo',
                'null_redirect': '> /dev/null',
                'error_redirect': '2>&1',
            }
        else:  # cmd
            return {
                'list_files': 'dir',
                'list_files_recursive': 'dir /s',
                'find_file': 'dir /s /b',
                'read_file': 'type',
                'create_dir': 'mkdir',
                'remove_file': 'del',
                'remove_dir': 'rmdir /s /q',
                'copy_file': 'copy',
                'move_file': 'move',
                'current_dir': 'cd',
                'change_dir': 'cd',
                'env_var': '%',
                'path_separator': '\\',
                'command_separator': '&',
                'pipe': '|',
                'grep': 'findstr',
                'cat': 'type',
                'echo': 'echo',
                'null_redirect': '> nul',
                'error_redirect': '2>&1',
            }
    
    def get_command(self, operation: str) -> str:
        """Get shell-appropriate command for an operation."""
        mappings = self.index.get('command_mappings', {})
        return mappings.get(operation, operation)
    
    def record_command_error(self, command: str, error: str, shell_type: str = None):
        """Record a command error for learning."""
        self.index['command_errors'].append({
            'command': command,
            'error': error[:500],
            'shell': shell_type or self.index.get('shell', {}).get('type', 'unknown'),
            'timestamp': datetime.now().isoformat()
        })
        # Keep only last 50 errors
        if len(self.index['command_errors']) > 50:
            self.index['command_errors'] = self.index['command_errors'][-50:]
        self._save_index()
    
    def get_command_suggestions(self) -> List[str]:
        """Get suggestions based on past command errors."""
        suggestions = []
        errors = self.index.get('command_errors', [])
        
        # Analyze recent errors for patterns
        for err in errors[-10:]:
            cmd = err.get('command', '')
            error_msg = err.get('error', '')
            
            if 'not recognized' in error_msg or 'command not found' in error_msg:
                suggestions.append(f"Command '{cmd}' not available - check shell type")
            elif 'permission denied' in error_msg.lower():
                suggestions.append(f"Permission issue with '{cmd}' - may need elevated privileges")
            elif 'syntax error' in error_msg.lower():
                suggestions.append(f"Syntax error in '{cmd}' - check shell-specific syntax")
        
        return list(set(suggestions))
    
    # ==================== PROJECT TREE INDEXING ====================
    
    def is_project_indexed(self, project_path: str) -> bool:
        """Check if a project has been indexed."""
        return project_path in self.index.get('projects_indexed', {})
    
    def get_project_index_path(self, project_path: str) -> Path:
        """Get path to project's index file (uses registry for consistent naming)."""
        project_memory_dir = self.get_project_memory_dir(project_path)
        return project_memory_dir / 'project_index.json'
    
    def index_project(self, project_path: str, force: bool = False) -> Dict:
        """Index a project's structure (runs once per project unless forced)."""
        project_path = str(Path(project_path).resolve())
        
        # Check if already indexed
        if not force and self.is_project_indexed(project_path):
            indexed_at = self.index['projects_indexed'][project_path].get('indexed_at')
            if indexed_at:
                # Check if index is less than 7 days old
                indexed_date = datetime.fromisoformat(indexed_at)
                if datetime.now() - indexed_date < timedelta(days=7):
                    return self.load_project_index(project_path)
        
        # Scan project
        project_index = self._scan_project(project_path)
        
        # Save project index
        index_path = self.get_project_index_path(project_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, 'w') as f:
            json.dump(project_index, f, indent=2)
        
        # Mark as indexed
        if 'projects_indexed' not in self.index:
            self.index['projects_indexed'] = {}
        self.index['projects_indexed'][project_path] = {
            'indexed_at': datetime.now().isoformat(),
            'index_path': str(index_path),
            'file_count': project_index.get('stats', {}).get('total_files', 0)
        }
        self.index['current_project'] = project_path
        self._save_index()
        
        return project_index
    
    def _scan_project(self, project_path: str) -> Dict:
        """Scan project directory structure."""
        project_dir = Path(project_path)
        
        # Skip patterns
        skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 
                     'dist', 'build', '.next', '.nuxt', 'target', 'bin', 'obj',
                     '.idea', '.vscode', 'coverage', '.pytest_cache'}
        skip_extensions = {'.pyc', '.pyo', '.exe', '.dll', '.so', '.dylib',
                          '.jpg', '.jpeg', '.png', '.gif', '.ico', '.svg',
                          '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4'}
        
        project_index = {
            'path': project_path,
            'name': project_dir.name,
            'type': 'unknown',
            'framework': None,
            'tree': {},
            'files': [],
            'directories': [],
            'key_files': {},
            'relationships': {},
            'stats': {
                'total_files': 0,
                'total_dirs': 0,
                'by_extension': {}
            },
            'indexed_at': datetime.now().isoformat()
        }
        
        # Detect project type
        project_index['type'], project_index['framework'] = self._detect_project_type(project_dir)
        
        # Build tree
        def scan_dir(dir_path: Path, rel_path: str = '') -> Dict:
            tree = {'_files': [], '_dirs': {}}
            
            try:
                for item in sorted(dir_path.iterdir()):
                    item_rel = f"{rel_path}/{item.name}" if rel_path else item.name
                    
                    if item.is_dir():
                        if item.name in skip_dirs or item.name.startswith('.'):
                            continue
                        tree['_dirs'][item.name] = scan_dir(item, item_rel)
                        project_index['directories'].append(item_rel)
                        project_index['stats']['total_dirs'] += 1
                    else:
                        if item.suffix.lower() in skip_extensions:
                            continue
                        tree['_files'].append(item.name)
                        project_index['files'].append(item_rel)
                        project_index['stats']['total_files'] += 1
                        
                        # Track by extension
                        ext = item.suffix.lower() or 'no_ext'
                        project_index['stats']['by_extension'][ext] = \
                            project_index['stats']['by_extension'].get(ext, 0) + 1
                        
                        # Identify key files
                        self._identify_key_file(item, item_rel, project_index)
            except PermissionError:
                pass
            
            return tree
        
        project_index['tree'] = scan_dir(project_dir)
        
        # Build relationships
        project_index['relationships'] = self._build_relationships(project_index)
        
        return project_index
    
    def _detect_project_type(self, project_dir: Path) -> tuple:
        """Detect project type and framework."""
        type_indicators = {
            'package.json': ('nodejs', None),
            'requirements.txt': ('python', None),
            'pyproject.toml': ('python', None),
            'Cargo.toml': ('rust', None),
            'go.mod': ('go', None),
            'pom.xml': ('java', 'maven'),
            'build.gradle': ('java', 'gradle'),
            'Gemfile': ('ruby', None),
            'composer.json': ('php', None),
        }
        
        framework_indicators = {
            'next.config.js': 'Next.js',
            'next.config.mjs': 'Next.js',
            'nuxt.config.js': 'Nuxt.js',
            'angular.json': 'Angular',
            'vue.config.js': 'Vue.js',
            'svelte.config.js': 'Svelte',
            'remix.config.js': 'Remix',
            'astro.config.mjs': 'Astro',
        }
        
        proj_type = 'unknown'
        framework = None
        
        for indicator, (ptype, fw) in type_indicators.items():
            if (project_dir / indicator).exists():
                proj_type = ptype
                framework = fw
                break
        
        for indicator, fw in framework_indicators.items():
            if (project_dir / indicator).exists():
                framework = fw
                break
        
        return proj_type, framework
    
    def _identify_key_file(self, file_path: Path, rel_path: str, project_index: Dict):
        """Identify key files in the project."""
        key_patterns = {
            'config': ['config', 'settings', '.env', 'tsconfig', 'jsconfig'],
            'entry': ['main', 'index', 'app', 'server', '__init__'],
            'package': ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod'],
            'readme': ['readme', 'README'],
            'test': ['test_', '_test', '.test.', '.spec.'],
            'types': ['.d.ts', 'types.ts', 'interfaces.ts'],
        }
        
        name_lower = file_path.name.lower()
        
        for category, patterns in key_patterns.items():
            for pattern in patterns:
                if pattern.lower() in name_lower:
                    if category not in project_index['key_files']:
                        project_index['key_files'][category] = []
                    project_index['key_files'][category].append(rel_path)
                    break
    
    def _build_relationships(self, project_index: Dict) -> Dict:
        """Build file relationships (imports, dependencies)."""
        relationships = {
            'entry_points': [],
            'config_files': project_index['key_files'].get('config', []),
            'test_files': project_index['key_files'].get('test', []),
            'directories_with_code': []
        }
        
        # Find directories with code files
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java'}
        dirs_with_code = set()
        
        for file_path in project_index['files']:
            ext = Path(file_path).suffix.lower()
            if ext in code_extensions:
                dir_path = str(Path(file_path).parent)
                if dir_path:
                    dirs_with_code.add(dir_path)
        
        relationships['directories_with_code'] = sorted(list(dirs_with_code))
        relationships['entry_points'] = project_index['key_files'].get('entry', [])[:5]
        
        return relationships
    
    def load_project_index(self, project_path: str) -> Optional[Dict]:
        """Load existing project index."""
        # Normalize path
        project_path = str(Path(project_path).resolve())
        
        # Try to get stored index path first
        if 'projects_indexed' not in self.index:
            self.index['projects_indexed'] = {}
        
        stored_info = self.index['projects_indexed'].get(project_path, {})
        if stored_info and stored_info.get('index_path'):
            stored_path = Path(stored_info['index_path'])
            if stored_path.exists():
                try:
                    with open(stored_path, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        # Fallback to calculated path
        index_path = self.get_project_index_path(project_path)
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def update_project_tree(self, project_path: str, file_path: str, action: str):
        """Update project tree when files change (create/modify/delete)."""
        project_index = self.load_project_index(project_path)
        if not project_index:
            return
        
        rel_path = str(Path(file_path).relative_to(project_path))
        
        if action == 'created':
            if rel_path not in project_index['files']:
                project_index['files'].append(rel_path)
                project_index['stats']['total_files'] += 1
                ext = Path(file_path).suffix.lower() or 'no_ext'
                project_index['stats']['by_extension'][ext] = \
                    project_index['stats']['by_extension'].get(ext, 0) + 1
        
        elif action == 'deleted':
            if rel_path in project_index['files']:
                project_index['files'].remove(rel_path)
                project_index['stats']['total_files'] -= 1
        
        project_index['last_updated'] = datetime.now().isoformat()
        
        # Save updated index
        index_path = self.get_project_index_path(project_path)
        with open(index_path, 'w') as f:
            json.dump(project_index, f, indent=2)
    
    # ==================== ENVIRONMENT DISCOVERY ====================
    
    def discover_environment(self, force: bool = False) -> Dict:
        """Discover environment details (cached for 24 hours)."""
        if not force and self.index.get('cache_valid_until'):
            try:
                valid_until = datetime.fromisoformat(self.index['cache_valid_until'])
                if datetime.now() < valid_until and self.index.get('environment'):
                    return self.index['environment']
            except:
                pass
        
        env = {
            'os': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine()
            },
            'python': {
                'version': platform.python_version(),
                'executable': os.sys.executable
            },
            'shell': self.detect_shell(),
            'user': {
                'name': os.getenv('USERNAME') or os.getenv('USER', 'unknown'),
                'home': str(Path.home()),
                'cwd': os.getcwd()
            },
            'tools': {},
            'discovered_at': datetime.now().isoformat()
        }
        
        # Check common tools
        tools = ['git', 'node', 'npm', 'npx', 'python', 'python3', 'pip', 'pip3', 'docker']
        for tool in tools:
            env['tools'][tool] = self._check_tool(tool)
        
        self.index['environment'] = env
        self.index['cache_valid_until'] = (datetime.now() + timedelta(hours=24)).isoformat()
        self._save_index()
        
        return env
    
    # ==================== CONTEXT SUMMARY ====================
    
    def get_context_summary(self, include_tree: bool = False) -> str:
        """Get summary of current context for injection."""
        parts = []
        
        # Shell info
        shell = self.index.get('shell', {})
        if shell:
            parts.append(f"[Shell: {shell.get('name', 'unknown')}]")
        
        # Environment
        env = self.index.get('environment', {})
        if env:
            os_info = env.get('os', {})
            parts.append(f"[OS: {os_info.get('system', 'unknown')}]")
            
            tools = env.get('tools', {})
            available = [t for t, info in tools.items() if info.get('available')]
            if available:
                parts.append(f"[Tools: {', '.join(available[:6])}]")
        
        # Current project
        current = self.index.get('current_project')
        if current:
            proj_info = self.index['projects_indexed'].get(current, {})
            parts.append(f"[Project: {Path(current).name} ({proj_info.get('file_count', '?')} files)]")
        
        # Command suggestions from errors
        suggestions = self.get_command_suggestions()
        if suggestions:
            parts.append(f"[Warnings: {len(suggestions)}]")
        
        return ' '.join(parts) if parts else '[No context]'
    
    def get_project_summary(self, project_path: str = None) -> str:
        """Get project tree summary for agents."""
        project_path = project_path or self.index.get('current_project')
        if not project_path:
            return '[No project indexed]'
        
        # Normalize path
        project_path = str(Path(project_path).resolve())
        
        proj = self.load_project_index(project_path)
        if not proj:
            return f'[Project {Path(project_path).name} not indexed]'
        
        lines = [
            f"Project: {proj['name']} ({proj['type']})",
            f"Framework: {proj['framework'] or 'none'}",
            f"Files: {proj['stats']['total_files']} | Dirs: {proj['stats']['total_dirs']}",
        ]
        
        # Key directories
        code_dirs = proj.get('relationships', {}).get('directories_with_code', [])[:5]
        if code_dirs:
            lines.append(f"Code in: {', '.join(code_dirs)}")
        
        # Entry points
        entries = proj.get('relationships', {}).get('entry_points', [])[:3]
        if entries:
            lines.append(f"Entry: {', '.join(entries)}")
        
        return ' | '.join(lines)


    def record_file_modified(self, file_path: str, tool_name: str):
        """Record a file modification."""
        if 'files_modified' not in self.index:
            self.index['files_modified'] = {}
        
        self.index['files_modified'][file_path] = {
            'modified_at': datetime.now().isoformat(),
            'by_tool': tool_name
        }
        
        # Keep only last 100 modifications
        if len(self.index['files_modified']) > 100:
            items = list(self.index['files_modified'].items())
            items.sort(key=lambda x: x[1].get('modified_at', ''))
            self.index['files_modified'] = dict(items[-100:])
        
        self._save_index()


    # ==================== FIRST-TIME PROJECT INITIALIZATION ====================
    
    def initialize_project_memory(self, project_path: str) -> Dict:
        """
        Initialize project memory for first-time use.
        Creates project folder, indexes structure, saves STRUCTURE.md.
        Returns initialization status with feedback messages.
        
        Uses REGISTRY for consistent project naming across sessions.
        """
        project_path = str(Path(project_path).resolve())
        project_name = Path(project_path).name
        
        # Use registry-based project memory directory (DETERMINISTIC)
        project_memory_dir = self.get_project_memory_dir(project_path)
        project_memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Create artifacts folder for agent outputs
        artifacts_dir = project_memory_dir / 'artifacts'
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if already initialized
        is_first_time = not self.is_project_indexed(project_path)
        
        # Feedback messages for visibility
        feedback = []
        
        if is_first_time:
            feedback.append(f"🆕 NEW PROJECT: {project_name}")
            feedback.append(f"📁 Creating memory folder: {project_memory_dir.name}")
        else:
            feedback.append(f"📂 EXISTING PROJECT: {project_name}")
            feedback.append(f"📁 Using memory folder: {project_memory_dir.name}")
        
        # Index the project
        project_index = self.index_project(project_path, force=is_first_time)
        
        file_count = project_index.get('stats', {}).get('total_files', 0)
        feedback.append(f"📊 Indexed {file_count} files")
        
        # Generate STRUCTURE.md for human readability
        structure_file = project_memory_dir / 'STRUCTURE.md'
        self._generate_structure_md(project_index, structure_file)
        feedback.append("✅ Generated STRUCTURE.md")
        
        # Create project-specific memory files if first time
        if is_first_time:
            self._create_project_memory_files(project_memory_dir, project_name)
            feedback.append("✅ Created lessons.yaml, mistakes.yaml, patterns.yaml")
        
        # Save quick-access file list
        files_json = project_memory_dir / 'files.json'
        with open(files_json, 'w') as f:
            json.dump({
                'files': project_index.get('files', []),
                'directories': project_index.get('directories', []),
                'key_files': project_index.get('key_files', {}),
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
        feedback.append("✅ Updated files.json")
        
        # Get project ID from registry for reference
        project_info = self.lookup_project(project_path)
        project_id = project_info.get('project_id', project_memory_dir.name) if project_info else project_memory_dir.name
        
        return {
            'project_id': project_id,  # Consistent ID for this project
            'project_name': project_name,
            'project_path': project_path,
            'memory_dir': str(project_memory_dir),
            'artifacts_dir': str(artifacts_dir),
            'is_first_time': is_first_time,
            'file_count': file_count,
            'type': project_index.get('type', 'unknown'),
            'framework': project_index.get('framework'),
            'feedback': feedback,  # Visible feedback messages
            'files_created': [
                'STRUCTURE.md',
                'files.json',
                'project_index.json',
                'lessons.yaml' if is_first_time else None,
                'mistakes.yaml' if is_first_time else None,
                'patterns.yaml' if is_first_time else None,
                'artifacts/' if is_first_time else None
            ]
        }

    # ==================== SESSION TRACKING (PROJECT-SPECIFIC) ====================
    
    def start_session(self, project_path: str, session_id: str) -> Dict:
        """
        Record session start for a project.
        
        PROJECT-SPECIFIC: Saves to project's sessions.json
        """
        project_path = str(Path(project_path).resolve())
        project_memory_dir = self.get_project_memory_dir(project_path)
        project_memory_dir.mkdir(parents=True, exist_ok=True)
        
        sessions_file = project_memory_dir / 'sessions.json'
        
        # Load existing sessions
        sessions = {'sessions': [], 'current': None}
        if sessions_file.exists():
            try:
                with open(sessions_file, 'r') as f:
                    sessions = json.load(f)
            except:
                pass
        
        # Create current session record
        current_session = {
            'session_id': session_id,
            'started_at': datetime.now().isoformat(),
            'ended_at': None,
            'agents_called': [],
            'files_modified': [],
            'status': 'active'
        }
        
        sessions['current'] = current_session
        
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        return current_session
    
    def end_session(self, project_path: str, session_id: str = None) -> Dict:
        """
        Record session end for a project.
        
        PROJECT-SPECIFIC: Updates project's sessions.json
        """
        project_path = str(Path(project_path).resolve())
        project_memory_dir = self.get_project_memory_dir(project_path)
        
        sessions_file = project_memory_dir / 'sessions.json'
        
        if not sessions_file.exists():
            return {'error': 'No sessions file'}
        
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
        
        current = sessions.get('current')
        if current:
            current['ended_at'] = datetime.now().isoformat()
            current['status'] = 'completed'
            
            # Move to history
            sessions['sessions'].append(current)
            sessions['current'] = None
            
            # Keep last 100 sessions
            if len(sessions['sessions']) > 100:
                sessions['sessions'] = sessions['sessions'][-100:]
        
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        return current or {}
    
    def record_agent_call(self, project_path: str, agent_name: str, prompt: str = ''):
        """
        Record an agent call in current session.
        
        PROJECT-SPECIFIC: Updates project's sessions.json current session
        """
        project_path = str(Path(project_path).resolve())
        project_memory_dir = self.get_project_memory_dir(project_path)
        
        sessions_file = project_memory_dir / 'sessions.json'
        
        if not sessions_file.exists():
            return
        
        try:
            with open(sessions_file, 'r') as f:
                sessions = json.load(f)
            
            current = sessions.get('current')
            if current:
                current['agents_called'].append({
                    'agent': agent_name,
                    'prompt': prompt[:100] if prompt else '',  # Truncate
                    'at': datetime.now().isoformat()
                })
                
                with open(sessions_file, 'w') as f:
                    json.dump(sessions, f, indent=2)
        except:
            pass
    
    def get_project_sessions(self, project_path: str, limit: int = 10) -> List[Dict]:
        """
        Get recent sessions for a project.
        
        PROJECT-SPECIFIC: Reads from project's sessions.json
        """
        project_path = str(Path(project_path).resolve())
        project_memory_dir = self.get_project_memory_dir(project_path)
        
        sessions_file = project_memory_dir / 'sessions.json'
        
        if not sessions_file.exists():
            return []
        
        try:
            with open(sessions_file, 'r') as f:
                sessions = json.load(f)
            return sessions.get('sessions', [])[-limit:]
        except:
            return []

    def _generate_structure_md(self, project_index: Dict, output_path: Path):
        """Generate human-readable STRUCTURE.md file."""
        lines = [
            f"# Project Structure: {project_index.get('name', 'Unknown')}",
            f"",
            f"**Type:** {project_index.get('type', 'unknown')}",
            f"**Framework:** {project_index.get('framework') or 'none'}",
            f"**Files:** {project_index.get('stats', {}).get('total_files', 0)}",
            f"**Directories:** {project_index.get('stats', {}).get('total_dirs', 0)}",
            f"**Indexed:** {project_index.get('indexed_at', 'unknown')}",
            f"",
            f"## Key Files",
            f""
        ]
        
        # Key files by category
        key_files = project_index.get('key_files', {})
        for category, files in key_files.items():
            lines.append(f"### {category.title()}")
            for f in files[:10]:  # Limit to 10 per category
                lines.append(f"- `{f}`")
            lines.append("")
        
        # Directory structure (top-level)
        lines.append("## Directory Structure")
        lines.append("")
        lines.append("```")
        
        tree = project_index.get('tree', {})
        self._format_tree(tree, lines, depth=0, max_depth=3)
        
        lines.append("```")
        lines.append("")
        
        # Code directories
        lines.append("## Code Locations")
        lines.append("")
        code_dirs = project_index.get('relationships', {}).get('directories_with_code', [])
        for d in code_dirs[:15]:
            lines.append(f"- `{d}/`")
        
        # Extension breakdown
        lines.append("")
        lines.append("## File Types")
        lines.append("")
        by_ext = project_index.get('stats', {}).get('by_extension', {})
        sorted_ext = sorted(by_ext.items(), key=lambda x: x[1], reverse=True)[:10]
        for ext, count in sorted_ext:
            lines.append(f"- `{ext}`: {count} files")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _format_tree(self, tree: Dict, lines: List[str], depth: int = 0, max_depth: int = 3):
        """Format tree structure for STRUCTURE.md."""
        if depth > max_depth:
            return
        
        indent = "  " * depth
        
        # Files first
        for f in tree.get('_files', [])[:5]:  # Limit files shown
            lines.append(f"{indent}├── {f}")
        
        if len(tree.get('_files', [])) > 5:
            lines.append(f"{indent}├── ... ({len(tree['_files']) - 5} more files)")
        
        # Then directories
        dirs = tree.get('_dirs', {})
        for i, (dir_name, subtree) in enumerate(list(dirs.items())[:10]):
            is_last = i == len(dirs) - 1 or i == 9
            prefix = "└──" if is_last else "├──"
            lines.append(f"{indent}{prefix} {dir_name}/")
            self._format_tree(subtree, lines, depth + 1, max_depth)
    
    def _create_project_memory_files(self, project_dir: Path, project_name: str):
        """Create project-specific memory files."""
        # Project lessons
        lessons_file = project_dir / 'lessons.yaml'
        if not lessons_file.exists():
            lessons_file.write_text(f"# Lessons learned for {project_name}\n# Auto-updated by dpt-memory\n\n")
        
        # Project mistakes
        mistakes_file = project_dir / 'mistakes.yaml'
        if not mistakes_file.exists():
            mistakes_file.write_text(f"# Mistakes to avoid for {project_name}\n# Auto-updated by dpt-memory\n\n")
        
        # Project patterns
        patterns_file = project_dir / 'patterns.yaml'
        if not patterns_file.exists():
            patterns_file.write_text(f"# Patterns for {project_name}\n# Auto-updated by dpt-memory\n\n")
    
    # ==================== FILE TARGETING FOR AGENTS ====================
    
    def get_files_by_pattern(self, project_path: str, pattern: str) -> List[str]:
        """Get files matching a pattern (for agents to target files without ls)."""
        project_index = self.load_project_index(project_path)
        if not project_index:
            return []
        
        import fnmatch
        pattern_lower = pattern.lower()
        matches = []
        
        for file_path in project_index.get('files', []):
            if fnmatch.fnmatch(file_path.lower(), pattern_lower):
                matches.append(file_path)
            elif pattern_lower in file_path.lower():
                matches.append(file_path)
        
        return matches
    
    def get_files_by_extension(self, project_path: str, extension: str) -> List[str]:
        """Get all files with a specific extension."""
        project_index = self.load_project_index(project_path)
        if not project_index:
            return []
        
        ext = extension.lower() if extension.startswith('.') else f'.{extension.lower()}'
        return [f for f in project_index.get('files', []) if f.lower().endswith(ext)]
    
    def get_file_path(self, project_path: str, filename: str) -> Optional[str]:
        """Get full path of a file by name (for agents to target exact file)."""
        project_index = self.load_project_index(project_path)
        if not project_index:
            return None
        
        filename_lower = filename.lower()
        for file_path in project_index.get('files', []):
            if Path(file_path).name.lower() == filename_lower:
                return str(Path(project_path) / file_path)
        return None
    
    def get_directory_contents(self, project_path: str, directory: str) -> Dict:
        """Get contents of a specific directory."""
        project_index = self.load_project_index(project_path)
        if not project_index:
            return {'files': [], 'dirs': []}
        
        dir_path = directory.strip('/').strip('\\')
        files = []
        dirs = set()
        
        for file_path in project_index.get('files', []):
            if file_path.startswith(dir_path + '/') or file_path.startswith(dir_path + '\\'):
                rel = file_path[len(dir_path)+1:]
                if '/' in rel or '\\' in rel:
                    # It's in a subdirectory
                    subdir = rel.split('/')[0].split('\\')[0]
                    dirs.add(subdir)
                else:
                    files.append(rel)
        
        return {'files': files, 'dirs': sorted(list(dirs))}
    
    # ==================== MISTAKE TRACKING (PROJECT-SPECIFIC) ====================
    
    def record_mistake(self, project_path: str, mistake: Dict):
        """
        Record a mistake for learning.
        
        PROJECT-SPECIFIC: Saves to project's mistakes.yaml
        GLOBAL (if high severity): Also saves to global mistakes.yaml
        """
        project_path = str(Path(project_path).resolve())
        
        # Use registry-based project memory directory (CONSISTENT)
        project_memory_dir = self.get_project_memory_dir(project_path)
        project_memory_dir.mkdir(parents=True, exist_ok=True)
        
        mistakes_file = project_memory_dir / 'mistakes.yaml'
        
        # Create entry
        entry = f"""
- id: mistake_{datetime.now().strftime('%Y%m%d%H%M%S')}
  date: {datetime.now().isoformat()}
  project: {Path(project_path).name}
  agent: {mistake.get('agent', 'unknown')}
  mistake: "{mistake.get('description', 'Unknown mistake')}"
  context: "{mistake.get('context', '')}"
  prevention: "{mistake.get('prevention', 'Be more careful')}"
  severity: {mistake.get('severity', 'medium')}
"""
        
        # Append to PROJECT-SPECIFIC file
        with open(mistakes_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # Also update GLOBAL mistakes if severe (for cross-project learning)
        if mistake.get('severity') == 'high':
            global_mistakes = self.memory_dir / 'global_mistakes.yaml'
            with open(global_mistakes, 'a', encoding='utf-8') as f:
                f.write(entry)
    
    def get_recent_mistakes(self, project_path: str, limit: int = 5) -> List[Dict]:
        """
        Get recent mistakes for a project.
        
        PROJECT-SPECIFIC: Reads from project's mistakes.yaml
        """
        project_path = str(Path(project_path).resolve())
        
        # Use registry-based project memory directory (CONSISTENT)
        project_memory_dir = self.get_project_memory_dir(project_path)
        
        mistakes_file = project_memory_dir / 'mistakes.yaml'
        if not mistakes_file.exists():
            return []
        
        mistakes = []
        content = mistakes_file.read_text()
        
        current = {}
        for line in content.split('\n'):
            if line.strip().startswith('- id:'):
                if current:
                    mistakes.append(current)
                current = {'id': line.split(':', 1)[1].strip()}
            elif ':' in line and current:
                key, value = line.strip().split(':', 1)
                key = key.strip().lstrip('- ')
                current[key] = value.strip().strip('"\'')
        
        if current:
            mistakes.append(current)
        
        return mistakes[-limit:]
    
    # ==================== INCREMENTAL UPDATE (PROJECT-SPECIFIC) ====================
    
    def update_on_file_change(self, project_path: str, file_path: str, action: str):
        """
        Update project index when a file changes.
        Called by hooks when agents create/modify/delete files.
        
        PROJECT-SPECIFIC: Updates project's files.json
        Actions: 'created', 'modified', 'deleted'
        """
        project_path = str(Path(project_path).resolve())
        
        # Update the tree
        self.update_project_tree(project_path, file_path, action)
        
        # Use registry-based project memory directory (CONSISTENT)
        project_memory_dir = self.get_project_memory_dir(project_path)
        
        project_index = self.load_project_index(project_path)
        if project_index:
            files_json = project_memory_dir / 'files.json'
            with open(files_json, 'w') as f:
                json.dump({
                    'files': project_index.get('files', []),
                    'directories': project_index.get('directories', []),
                    'key_files': project_index.get('key_files', {}),
                    'updated_at': datetime.now().isoformat(),
                    'last_change': {
                        'file': file_path,
                        'action': action
                    }
                }, f, indent=2)
        
        # Track modification (GLOBAL - for cross-project file tracking)
        self.record_file_modified(file_path, f'agent_{action}')


# ==================== PATTERN RECOGNITION SYSTEM ====================
# Inspired by ML: Recognize patterns with confidence scores (0.0 to 1.0)

class PatternRecognizer:
    """
    ML-inspired pattern recognition for agent selection.
    
    Like a neural network:
    - Input: User prompt (text)
    - Weights: Keyword patterns for each agent
    - Output: Confidence scores (0.0 to 1.0) for each agent
    - Threshold: Minimum score to trigger agent call
    """
    
    # Agent patterns with weights (higher = more important)
    AGENT_PATTERNS = {
        'dpt-memory': {
            'keywords': ['remember', 'learn', 'lesson', 'mistake', 'context', 'history', 
                        'previous', 'last time', 'before', 'session', 'save', 'store'],
            'weight': 1.0,  # Critical agent
            'threshold': 0.1,  # Low threshold - almost always needed
            'triggers': {
                'start_session': ['start', 'begin', 'new task', 'initialize'],
                'end_session': ['done', 'complete', 'finish', 'end', 'summary']
            }
        },
        'dpt-research': {
            'keywords': ['research', 'investigate', 'find out', 'best practice', 'how to',
                        'what is', 'learn about', 'explore', 'study', 'analyze', 'understand'],
            'weight': 0.8,
            'threshold': 0.3
        },
        'dpt-product': {
            'keywords': ['requirement', 'feature', 'user story', 'prd', 'spec', 'product',
                        'acceptance criteria', 'stakeholder', 'business', 'mvp'],
            'weight': 0.7,
            'threshold': 0.4
        },
        'dpt-arch': {
            'keywords': ['architecture', 'design', 'structure', 'pattern', 'system',
                        'component', 'module', 'layer', 'diagram', 'tech stack', 'scalab'],
            'weight': 0.8,
            'threshold': 0.35
        },
        'dpt-scrum': {
            'keywords': ['task', 'breakdown', 'sprint', 'story', 'epic', 'backlog',
                        'estimate', 'priority', 'plan', 'decompose', 'steps'],
            'weight': 0.7,
            'threshold': 0.35
        },
        'dpt-dev': {
            'keywords': ['implement', 'code', 'build', 'create', 'develop', 'write',
                        'fix', 'bug', 'feature', 'function', 'class', 'method', 'refactor'],
            'weight': 0.9,
            'threshold': 0.2  # Low threshold - often needed
        },
        'dpt-data': {
            'keywords': ['database', 'db', 'sql', 'query', 'schema', 'migration', 'table',
                        'model', 'orm', 'postgres', 'mysql', 'mongodb', 'prisma', 'data'],
            'weight': 0.85,
            'threshold': 0.4
        },
        'dpt-api': {
            'keywords': ['api', 'endpoint', 'rest', 'graphql', 'route', 'controller',
                        'http', 'request', 'response', 'swagger', 'openapi'],
            'weight': 0.85,
            'threshold': 0.4
        },
        'dpt-ux': {
            'keywords': ['ui', 'ux', 'frontend', 'component', 'page', 'form', 'button',
                        'layout', 'css', 'style', 'react', 'vue', 'interface', 'design',
                        'user experience', 'responsive', 'accessibility'],
            'weight': 0.8,
            'threshold': 0.35
        },
        'dpt-qa': {
            'keywords': ['test', 'verify', 'check', 'validate', 'qa', 'quality',
                        'bug', 'issue', 'unit test', 'integration', 'e2e', 'coverage'],
            'weight': 0.85,
            'threshold': 0.3
        },
        'dpt-sec': {
            'keywords': ['security', 'auth', 'login', 'password', 'token', 'jwt', 'oauth',
                        'encrypt', 'vulnerab', 'owasp', 'xss', 'csrf', 'injection', 'hack'],
            'weight': 0.9,
            'threshold': 0.35
        },
        'dpt-perf': {
            'keywords': ['performance', 'optimize', 'speed', 'slow', 'fast', 'cache',
                        'memory', 'benchmark', 'profil', 'latency', 'throughput'],
            'weight': 0.75,
            'threshold': 0.4
        },
        'dpt-lead': {
            'keywords': ['review', 'code review', 'approve', 'merge', 'pr', 'pull request',
                        'feedback', 'suggest', 'improve', 'quality'],
            'weight': 0.7,
            'threshold': 0.4
        },
        'dpt-ops': {
            'keywords': ['deploy', 'ci', 'cd', 'docker', 'kubernetes', 'pipeline', 'aws',
                        'azure', 'server', 'nginx', 'hosting', 'devops', 'infrastructure'],
            'weight': 0.8,
            'threshold': 0.4
        },
        'dpt-docs': {
            'keywords': ['document', 'readme', 'guide', 'tutorial', 'comment', 'jsdoc',
                        'explain', 'documentation', 'wiki', 'manual'],
            'weight': 0.6,
            'threshold': 0.45
        },
        'dpt-grammar': {
            'keywords': ['grammar', 'spelling', 'writing', 'text', 'prose', 'english',
                        'tone', 'clarity', 'readable'],
            'weight': 0.5,
            'threshold': 0.5
        },
        'dpt-review': {
            'keywords': ['simplify', 'simple', 'clean', 'refactor', 'complexity',
                        'readable', 'maintainable', 'elegant'],
            'weight': 0.65,
            'threshold': 0.4
        },
        'dpt-output': {
            'keywords': ['summarize', 'summary', 'report', 'output', 'result', 'final',
                        'conclusion', 'wrap up'],
            'weight': 0.9,
            'threshold': 0.3
        }
    }
    
    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or Path(os.path.expanduser('~/.factory/memory'))
        self.recognition_file = self.memory_dir / 'recognition_history.json'
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load recognition history for learning."""
        if self.recognition_file.exists():
            try:
                with open(self.recognition_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'recognitions': [],
            'accuracy_feedback': [],
            'adjusted_weights': {}
        }
    
    def _save_history(self):
        """Save recognition history."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        with open(self.recognition_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def calculate_confidence(self, prompt: str, agent: str) -> float:
        """
        Calculate confidence score (0.0 to 1.0) for an agent given a prompt.
        
        Like a neural network's softmax output:
        - More keyword matches = higher score
        - Weighted by keyword importance
        - Normalized to 0.0-1.0 range
        """
        if agent not in self.AGENT_PATTERNS:
            return 0.0
        
        pattern = self.AGENT_PATTERNS[agent]
        keywords = pattern['keywords']
        weight = pattern['weight']
        
        # Check for adjusted weights from learning
        if agent in self.history.get('adjusted_weights', {}):
            weight = self.history['adjusted_weights'][agent]
        
        prompt_lower = prompt.lower()
        
        # Count keyword matches
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            if keyword in prompt_lower:
                matches += 1
                # Bonus for exact word match (not substring)
                words = prompt_lower.split()
                if keyword in words:
                    matches += 0.5
        
        # Calculate base score
        if total_keywords == 0:
            base_score = 0.0
        else:
            base_score = matches / total_keywords
        
        # Apply weight
        weighted_score = base_score * weight
        
        # Normalize to 0.0-1.0 (cap at 1.0)
        confidence = min(1.0, weighted_score)
        
        return round(confidence, 3)
    
    def recognize_agents(self, prompt: str) -> Dict[str, float]:
        """
        Recognize which agents should be called based on prompt.
        Returns dict of agent -> confidence score.
        
        Like multi-label classification:
        - Multiple agents can have high scores
        - Only agents above threshold are recommended
        """
        scores = {}
        
        for agent in self.AGENT_PATTERNS:
            confidence = self.calculate_confidence(prompt, agent)
            threshold = self.AGENT_PATTERNS[agent]['threshold']
            
            if confidence >= threshold:
                scores[agent] = confidence
        
        # Sort by confidence (highest first)
        sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_scores
    
    def get_recommended_agents(self, prompt: str, min_confidence: float = 0.0) -> List[str]:
        """Get list of recommended agents above minimum confidence."""
        scores = self.recognize_agents(prompt)
        return [agent for agent, score in scores.items() if score >= min_confidence]
    
    def should_call_agent(self, prompt: str, agent: str) -> tuple:
        """
        Determine if a specific agent should be called.
        Returns: (should_call: bool, confidence: float, reason: str)
        """
        confidence = self.calculate_confidence(prompt, agent)
        threshold = self.AGENT_PATTERNS.get(agent, {}).get('threshold', 0.5)
        
        should_call = confidence >= threshold
        
        if should_call:
            reason = f"Confidence {confidence:.2f} >= threshold {threshold:.2f}"
        else:
            reason = f"Confidence {confidence:.2f} < threshold {threshold:.2f}"
        
        return should_call, confidence, reason
    
    def record_recognition(self, prompt: str, recognized_agents: Dict[str, float], 
                          actually_used: List[str] = None):
        """
        Record a recognition event for learning.
        Compare predicted vs actual to improve weights over time.
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'prompt_hash': hash(prompt) % 100000,
            'recognized': recognized_agents,
            'actually_used': actually_used or [],
            'prompt_length': len(prompt)
        }
        
        self.history['recognitions'].append(record)
        
        # Keep only last 100 recognitions
        if len(self.history['recognitions']) > 100:
            self.history['recognitions'] = self.history['recognitions'][-100:]
        
        self._save_history()
    
    def provide_feedback(self, agent: str, was_helpful: bool):
        """
        Provide feedback on whether agent call was helpful.
        This adjusts weights for future recognition (like gradient descent).
        """
        self.history['accuracy_feedback'].append({
            'agent': agent,
            'helpful': was_helpful,
            'timestamp': datetime.now().isoformat()
        })
        
        # Adjust weight based on feedback (simple learning rule)
        if agent not in self.history['adjusted_weights']:
            base_weight = self.AGENT_PATTERNS.get(agent, {}).get('weight', 0.5)
            self.history['adjusted_weights'][agent] = base_weight
        
        current_weight = self.history['adjusted_weights'][agent]
        
        # Small adjustment (like learning rate in ML)
        learning_rate = 0.05
        if was_helpful:
            self.history['adjusted_weights'][agent] = min(1.0, current_weight + learning_rate)
        else:
            self.history['adjusted_weights'][agent] = max(0.1, current_weight - learning_rate)
        
        self._save_history()
    
    def get_recognition_summary(self, prompt: str) -> str:
        """Get human-readable summary of agent recognition."""
        scores = self.recognize_agents(prompt)
        
        if not scores:
            return "[No agents recognized for this prompt]"
        
        lines = ["[Agent Recognition Scores]"]
        for agent, score in scores.items():
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            lines.append(f"  {agent}: {bar} {score:.2f}")
        
        return "\n".join(lines)


# Convenience function for pattern recognition
def get_pattern_recognizer() -> PatternRecognizer:
    return PatternRecognizer()


def recognize_agents_for_prompt(prompt: str) -> Dict[str, float]:
    """Quick function to get agent recognition scores."""
    return PatternRecognizer().recognize_agents(prompt)


# Convenience functions
def get_context_index() -> ContextIndex:
    return ContextIndex()

def get_shell_command(operation: str) -> str:
    return ContextIndex().get_command(operation)

def index_current_project(force: bool = False) -> Dict:
    ci = ContextIndex()
    return ci.index_project(os.getcwd(), force=force)

def initialize_project(project_path: str = None) -> Dict:
    """Initialize project memory (called on first use)."""
    ci = ContextIndex()
    return ci.initialize_project_memory(project_path or os.getcwd())

def find_file(filename: str, project_path: str = None) -> Optional[str]:
    """Find a file by name without ls/find commands."""
    ci = ContextIndex()
    return ci.get_file_path(project_path or os.getcwd(), filename)

def list_files(pattern: str = '*', project_path: str = None) -> List[str]:
    """List files matching pattern without ls command."""
    ci = ContextIndex()
    return ci.get_files_by_pattern(project_path or os.getcwd(), pattern)


if __name__ == '__main__':
    ci = ContextIndex()
    env = ci.discover_environment(force=True)
    print(f"Shell: {ci.index['shell']}")
    print(f"Command for 'list_files': {ci.get_command('list_files')}")
    print(f"\nContext: {ci.get_context_summary()}")
    
    # Test project initialization
    result = ci.initialize_project_memory(os.getcwd())
    print(f"\nProject initialized: {result}")
