# Cross-Platform Command Reference

Quick reference for platform-specific commands. Always detect platform first!

## Detect Platform (Native Commands - No Dependencies)

### Method 1: Try Native Commands

```bash
# Windows (CMD or PowerShell)
echo %OS%
# Output: Windows_NT

# Linux/macOS
uname -s
# Output: Linux or Darwin
```

### Method 2: Check What Works

| Command | Windows | Linux | macOS |
|---------|---------|-------|-------|
| `echo %OS%` | ✅ `Windows_NT` | ❌ Empty | ❌ Empty |
| `uname -s` | ❌ Error | ✅ `Linux` | ✅ `Darwin` |

**Simple detection logic:**
1. Try `uname -s` - if it returns `Linux` or `Darwin`, you're on Unix
2. If `uname` fails, you're on Windows

### Method 3: Node.js (if available)

```bash
node -e "console.log(process.platform, process.arch)"
# Output: win32 x64, darwin arm64, linux x64
```

| OS | `uname -s` | `%OS%` | `process.platform` |
|----|------------|--------|-------------------|
| Windows | ❌ | `Windows_NT` | `win32` |
| macOS | `Darwin` | ❌ | `darwin` |
| Linux | `Linux` | ❌ | `linux` |

## Common Commands

### Get Current Date

| Platform | Command | Format |
|----------|---------|--------|
| Windows CMD | `date /t` | `Sat 12/07/2025` |
| Windows PS | `Get-Date -Format "yyyy-MM-dd"` | `2025-12-07` |
| Linux/macOS | `date +"%Y-%m-%d"` | `2025-12-07` |
| Node.js (all) | `node -e "console.log(new Date().toISOString().split('T')[0])"` | `2025-12-07` |

### Get Current Time

| Platform | Command |
|----------|---------|
| Windows CMD | `time /t` |
| Windows PS | `Get-Date -Format "HH:mm:ss"` |
| Linux/macOS | `date +"%H:%M:%S"` |

### System Information

| Task | Windows | Linux | macOS |
|------|---------|-------|-------|
| OS Version | `ver` | `uname -a` | `sw_vers` |
| Architecture | `echo %PROCESSOR_ARCHITECTURE%` | `uname -m` | `uname -m` |
| Hostname | `hostname` | `hostname` | `hostname` |
| Username | `echo %USERNAME%` | `whoami` | `whoami` |
| Home Dir | `echo %USERPROFILE%` | `echo $HOME` | `echo $HOME` |

### File Operations

| Task | Windows CMD | Linux/macOS |
|------|-------------|-------------|
| List files | `dir` | `ls -la` |
| Current dir | `cd` | `pwd` |
| Copy file | `copy src dest` | `cp src dest` |
| Move file | `move src dest` | `mv src dest` |
| Delete file | `del file` | `rm file` |
| Make dir | `mkdir dir` | `mkdir dir` |
| Remove dir | `rmdir /s dir` | `rm -rf dir` |

### Process Management

| Task | Windows | Linux/macOS |
|------|---------|-------------|
| List processes | `tasklist` | `ps aux` |
| Kill process | `taskkill /PID 1234` | `kill 1234` |
| Find process | `tasklist \| findstr name` | `ps aux \| grep name` |

### Network

| Task | Windows | Linux/macOS |
|------|---------|-------------|
| IP address | `ipconfig` | `ifconfig` or `ip addr` |
| Ports in use | `netstat -an` | `netstat -an` or `ss -tuln` |
| Ping | `ping host` | `ping host` |
| DNS lookup | `nslookup domain` | `dig domain` or `nslookup domain` |

### Disk Usage

| Task | Windows | Linux/macOS |
|------|---------|-------------|
| Disk space | `wmic logicaldisk get size,freespace` | `df -h` |
| Folder size | `dir /s` | `du -sh *` |

### Environment Variables

| Task | Windows CMD | Windows PS | Linux/macOS |
|------|-------------|------------|-------------|
| View all | `set` | `Get-ChildItem Env:` | `env` |
| View one | `echo %VAR%` | `$env:VAR` | `echo $VAR` |
| Set temp | `set VAR=value` | `$env:VAR="value"` | `export VAR=value` |

## Node.js Cross-Platform Code

```javascript
const os = require('os');
const path = require('path');

// Platform detection
const platform = process.platform;  // 'win32', 'darwin', 'linux'
const arch = process.arch;          // 'x64', 'arm64'
const isWindows = platform === 'win32';
const isMac = platform === 'darwin';
const isLinux = platform === 'linux';

// Safe paths (ALWAYS use these)
const homeDir = os.homedir();
const tempDir = os.tmpdir();
const configPath = path.join(homeDir, '.config', 'myapp');

// Path separator
const sep = path.sep;  // '\\' on Windows, '/' on Unix

// Line endings
const EOL = os.EOL;  // '\r\n' on Windows, '\n' on Unix
```

## Best Practices

1. **Always detect platform** before running shell commands
2. **Use Node.js** built-in modules (`os`, `path`) when possible
3. **Use `path.join()`** for file paths, never string concatenation
4. **Test on all platforms** or document platform requirements
5. **Provide alternatives** when a command differs by platform
