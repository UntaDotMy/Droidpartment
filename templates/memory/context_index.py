#!/usr/bin/env python3
"""
Context Indexer for Droidpartment (Enhanced v3)
Indexes project structure, caches context, provides shell-aware commands.

Features:
- First-time project detection and initialization
- Project memory folder creation
- Human-readable STRUCTURE.md generation
- Live incremental updates when files change
- File targeting without ls/find commands
- Shell-aware command suggestions
- Mistake tracking with prevention learning

Pure Python stdlib - no external dependencies.
"""

import json
import os
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class ContextIndex:
    """Indexes and caches context for efficient agent access."""
    
    def __init__(self, memory_dir: Optional[Path] = None):
        self.memory_dir = memory_dir or Path(os.path.expanduser('~/.factory/memory'))
        self.index_file = self.memory_dir / 'context_index.json'
        self.projects_dir = self.memory_dir / 'projects'
        self.index = self._load_index()
    
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
        """Get path to project's index file."""
        project_name = Path(project_path).name
        project_hash = hash(project_path) % 10000
        return self.projects_dir / f"{project_name}_{project_hash}" / 'project_index.json'
    
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
        Returns initialization status.
        """
        project_path = str(Path(project_path).resolve())
        project_name = Path(project_path).name
        
        # Create project memory folder
        project_memory_dir = self.projects_dir / f"{project_name}_{hash(project_path) % 10000}"
        project_memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if already initialized
        is_first_time = not self.is_project_indexed(project_path)
        
        # Index the project
        project_index = self.index_project(project_path, force=is_first_time)
        
        # Generate STRUCTURE.md for human readability
        structure_file = project_memory_dir / 'STRUCTURE.md'
        self._generate_structure_md(project_index, structure_file)
        
        # Create project-specific memory files if first time
        if is_first_time:
            self._create_project_memory_files(project_memory_dir, project_name)
        
        # Save quick-access file list
        files_json = project_memory_dir / 'files.json'
        with open(files_json, 'w') as f:
            json.dump({
                'files': project_index.get('files', []),
                'directories': project_index.get('directories', []),
                'key_files': project_index.get('key_files', {}),
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
        
        return {
            'project_name': project_name,
            'project_path': project_path,
            'memory_dir': str(project_memory_dir),
            'is_first_time': is_first_time,
            'file_count': project_index.get('stats', {}).get('total_files', 0),
            'type': project_index.get('type', 'unknown'),
            'framework': project_index.get('framework')
        }
    
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
    
    # ==================== MISTAKE TRACKING ====================
    
    def record_mistake(self, project_path: str, mistake: Dict):
        """Record a mistake for learning."""
        project_path = str(Path(project_path).resolve())
        project_name = Path(project_path).name
        project_memory_dir = self.projects_dir / f"{project_name}_{hash(project_path) % 10000}"
        
        mistakes_file = project_memory_dir / 'mistakes.yaml'
        
        # Create entry
        entry = f"""
- id: mistake_{datetime.now().strftime('%Y%m%d%H%M%S')}
  date: {datetime.now().isoformat()}
  agent: {mistake.get('agent', 'unknown')}
  mistake: "{mistake.get('description', 'Unknown mistake')}"
  context: "{mistake.get('context', '')}"
  prevention: "{mistake.get('prevention', 'Be more careful')}"
  severity: {mistake.get('severity', 'medium')}
"""
        
        # Append to file
        with open(mistakes_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # Also update global mistakes if severe
        if mistake.get('severity') == 'high':
            global_mistakes = self.memory_dir / 'mistakes.yaml'
            with open(global_mistakes, 'a', encoding='utf-8') as f:
                f.write(entry)
    
    def get_recent_mistakes(self, project_path: str, limit: int = 5) -> List[Dict]:
        """Get recent mistakes for a project."""
        project_path = str(Path(project_path).resolve())
        project_name = Path(project_path).name
        project_memory_dir = self.projects_dir / f"{project_name}_{hash(project_path) % 10000}"
        
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
    
    # ==================== INCREMENTAL UPDATE ====================
    
    def update_on_file_change(self, project_path: str, file_path: str, action: str):
        """
        Update project index when a file changes.
        Called by hooks when agents create/modify/delete files.
        
        Actions: 'created', 'modified', 'deleted'
        """
        project_path = str(Path(project_path).resolve())
        
        # Update the tree
        self.update_project_tree(project_path, file_path, action)
        
        # Update files.json
        project_name = Path(project_path).name
        project_memory_dir = self.projects_dir / f"{project_name}_{hash(project_path) % 10000}"
        
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
        
        # Track modification
        self.record_file_modified(file_path, f'agent_{action}')


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
