#!/usr/bin/env python3
"""
Factory Droid Hook: PreToolUse
Triggers before a tool call is executed.

Features:
- Tool validation and safety checks
- Command validation for Bash/Execute tools
- File path protection for sensitive files
- Permission decisions (allow/deny/ask)

Input: JSON from stdin with tool_name, tool_input
Output: JSON with permissionDecision and optional updatedInput

Per Factory AI specification:
- permissionDecision: "allow" | "deny" | "ask"
- permissionDecisionReason: Shown to user (allow/ask) or Droid (deny)
- updatedInput: Optional modified tool input
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

# Patterns for dangerous commands
DANGEROUS_COMMANDS = [
    r'\brm\s+-rf\s+[/~]',      # rm -rf / or ~
    r'\bsudo\s+rm\b',          # sudo rm
    r'\bformat\b.*[cCdD]:',    # format C: or D:
    r'\bdel\s+/[sS]\s+/[qQ]',  # del /s /q (Windows)
    r'\brmdir\s+/[sS]\s+/[qQ]',# rmdir /s /q (Windows)
    r'>\s*/dev/sd[a-z]',       # Overwrite disk
    r'\bdd\s+if=.*of=/dev/',   # dd to device
    r'\bmkfs\b',               # Make filesystem
    r'\bchmod\s+-R\s+777\s+/', # chmod 777 on root
]

# Protected file patterns
PROTECTED_FILES = [
    r'\.env$',                 # Environment files
    r'\.env\.local$',
    r'\.env\.production$',
    r'secrets?\.(json|yaml|yml)$',
    r'credentials?\.(json|yaml|yml)$',
    r'\.pem$',                 # SSL certificates
    r'\.key$',                 # Private keys
    r'id_rsa',                 # SSH keys
    r'\.ssh/config$',
]

# Files that should trigger "ask" instead of auto-allow
SENSITIVE_FILES = [
    r'package\.json$',
    r'package-lock\.json$',
    r'yarn\.lock$',
    r'Dockerfile$',
    r'docker-compose\.ya?ml$',
    r'\.github/workflows/',
    r'Makefile$',
    r'requirements\.txt$',
]


def is_dangerous_command(command: str) -> tuple:
    """Check if command matches dangerous patterns."""
    for pattern in DANGEROUS_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, pattern
    return False, None


def is_protected_file(file_path: str) -> bool:
    """Check if file is in protected list."""
    for pattern in PROTECTED_FILES:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def is_sensitive_file(file_path: str) -> bool:
    """Check if file is sensitive (needs user confirmation)."""
    for pattern in SENSITIVE_FILES:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def validate_bash_tool(tool_input: dict) -> dict:
    """Validate Bash/Execute tool calls."""
    command = tool_input.get('command', '')
    
    # Check for dangerous commands
    is_dangerous, pattern = is_dangerous_command(command)
    if is_dangerous:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Dangerous command pattern detected: {pattern}. This command could cause data loss."
            }
        }
    
    # Allow safe commands
    return None


def validate_file_tool(tool_input: dict, tool_name: str) -> dict:
    """Validate file operation tools (Write, Edit, Create)."""
    file_path = tool_input.get('file_path', '') or tool_input.get('path', '')
    
    # Check for protected files
    if is_protected_file(file_path):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Cannot modify protected file: {file_path}. This file contains sensitive data."
            }
        }
    
    # Check for sensitive files - ask user
    if is_sensitive_file(file_path):
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"Modifying sensitive file: {file_path}. Please confirm this change."
            }
        }
    
    return None


def record_tool_usage(tool_name: str, tool_input: dict):
    """Record tool usage for analytics."""
    try:
        stats_file = memory_dir / 'tool_usage.json'
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {'total_calls': 0, 'tools': {}, 'blocked': 0}
        
        stats['total_calls'] += 1
        stats['last_call'] = datetime.now().isoformat()
        
        if tool_name not in stats['tools']:
            stats['tools'][tool_name] = 0
        stats['tools'][tool_name] += 1
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
            
    except:
        pass  # Silent fail


def main():
    try:
        # Read input from Droid (Factory AI PreToolUse format)
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Record tool usage
        record_tool_usage(tool_name, tool_input)
        
        # Validate based on tool type
        result = None
        
        if tool_name in ['Bash', 'Execute']:
            result = validate_bash_tool(tool_input)
        
        elif tool_name in ['Write', 'Edit', 'Create']:
            result = validate_file_tool(tool_input, tool_name)
        
        # Output result if validation failed
        if result:
            # Update blocked count
            try:
                stats_file = memory_dir / 'tool_usage.json'
                if stats_file.exists():
                    with open(stats_file, 'r') as f:
                        stats = json.load(f)
                    stats['blocked'] = stats.get('blocked', 0) + 1
                    with open(stats_file, 'w') as f:
                        json.dump(stats, f, indent=2)
            except:
                pass
            
            print(json.dumps(result))
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        # Silent fail - don't interrupt Droid
        sys.exit(0)


if __name__ == '__main__':
    main()
