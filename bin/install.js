#!/usr/bin/env node
/**
 * Droidpartment CLI Installer v2.0 - MANIFEST-BASED
 * 
 * Features:
 *   - Tracks all installed files with MD5 hashes
 *   - Clean uninstall removes exactly what was installed
 *   - Update detects and removes stale files from old versions
 *   - Settings.json modifications are tracked and reversible
 * 
 * Commands:
 *   npx droidpartment                 # Interactive install/update
 *   npx droidpartment install         # Install to ~/.factory
 *   npx droidpartment update          # Update existing installation
 *   npx droidpartment uninstall       # Remove installation
 *   npx droidpartment status          # Check installation status
 *   npx droidpartment reinstall       # Uninstall + fresh install
 *   npx droidpartment memory          # Manage memory files
 * 
 * Flags:
 *   -y, --yes          Auto-confirm all prompts
 *   -q, --quiet        Minimal output
 *   -v, --verbose      Detailed output
 *   --project          Install to ./.factory instead of ~/.factory
 *   --force            Force overwrite even if same version
 *   --dry-run          Show what would happen without making changes
 *   --purge            Delete memory when uninstalling
 *   --version          Show version
 *   --help             Show help
 * 
 * Exit codes:
 *   0 = Success
 *   1 = General error
 *   2 = Invalid arguments
 *   3 = Not installed (for status/update/uninstall)
 *   4 = Already installed (for install without --force)
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const readline = require('readline');

// === CONFIGURATION ===
const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');
const PERSONAL_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.factory');
const PROJECT_DIR = path.join(process.cwd(), '.factory');
const MANIFEST_FILE = '.droidpartment-manifest.json';

// Get version from package.json
const PACKAGE_JSON = require(path.join(__dirname, '..', 'package.json'));
const CURRENT_VERSION = PACKAGE_JSON.version;

// Exit codes (following CLI best practices)
const EXIT_SUCCESS = 0;
const EXIT_ERROR = 1;
const EXIT_INVALID_ARGS = 2;
const EXIT_NOT_INSTALLED = 3;
const EXIT_ALREADY_INSTALLED = 4;

const COLORS = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    red: '\x1b[31m',
    gray: '\x1b[90m'
};

// Logging with verbosity levels
let VERBOSITY = 1; // 0=quiet, 1=normal, 2=verbose
let DRY_RUN = false;

const log = {
    info: (msg) => VERBOSITY >= 1 && console.log(`${COLORS.blue}ℹ${COLORS.reset} ${msg}`),
    success: (msg) => VERBOSITY >= 1 && console.log(`${COLORS.green}✓${COLORS.reset} ${msg}`),
    warn: (msg) => VERBOSITY >= 1 && console.log(`${COLORS.yellow}⚠${COLORS.reset} ${msg}`),
    error: (msg) => console.error(`${COLORS.red}✗${COLORS.reset} ${msg}`), // Always show errors
    header: (msg) => VERBOSITY >= 1 && console.log(`\n${COLORS.bright}${COLORS.cyan}${msg}${COLORS.reset}\n`),
    verbose: (msg) => VERBOSITY >= 2 && console.log(`${COLORS.gray}  ${msg}${COLORS.reset}`),
    dryRun: (msg) => DRY_RUN && console.log(`${COLORS.yellow}[DRY-RUN]${COLORS.reset} ${msg}`)
};

// === MANIFEST SYSTEM ===
// The manifest tracks every file we install so we can cleanly remove them

function getFileHash(filePath) {
    if (!fs.existsSync(filePath)) return null;
    const content = fs.readFileSync(filePath);
    return crypto.createHash('md5').update(content).digest('hex');
}

function loadManifest(targetDir) {
    const manifestPath = path.join(targetDir, MANIFEST_FILE);
    if (fs.existsSync(manifestPath)) {
        try {
            return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
        } catch (e) {
            return null;
        }
    }
    return null;
}

function saveManifest(targetDir, manifest) {
    const manifestPath = path.join(targetDir, MANIFEST_FILE);
    fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
}

function createManifest(version) {
    return {
        version: version,
        installedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        files: {},           // relativePath -> { hash, size, type }
        directories: [],     // directories we created
        settingsModified: false,
        hooksRegistered: []
    };
}

function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

// Copy directory and track all files in manifest
function copyDirWithManifest(src, dest, manifest, baseDir) {
    ensureDir(dest);
    const entries = fs.readdirSync(src, { withFileTypes: true });
    let copied = 0;
    
    // Track the directory itself
    const relDir = path.relative(baseDir, dest);
    if (relDir && !manifest.directories.includes(relDir)) {
        manifest.directories.push(relDir);
    }
    
    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        
        if (entry.isDirectory()) {
            copied += copyDirWithManifest(srcPath, destPath, manifest, baseDir);
        } else {
            // DON'T overwrite learning files if they exist (preserve user data)
            const learningFiles = ['lessons.yaml', 'mistakes.yaml', 'patterns.yaml', 'stats.yaml'];
            const isLearningFile = learningFiles.includes(entry.name);
            
            if (isLearningFile && fs.existsSync(destPath)) {
                // Skip - preserve existing learning data
                // But still track in manifest
                const relPath = path.relative(baseDir, destPath);
                const hash = getFileHash(destPath);
                const stats = fs.statSync(destPath);
                manifest.files[relPath] = { hash, size: stats.size, type: 'yaml' };
            } else {
                fs.copyFileSync(srcPath, destPath);
                copied++;
            }
            
            // Track file in manifest
            const relPath = path.relative(baseDir, destPath);
            const hash = getFileHash(destPath);
            const stats = fs.statSync(destPath);
            
            manifest.files[relPath] = {
                hash: hash,
                size: stats.size,
                type: path.extname(entry.name).slice(1) || 'unknown'
            };
        }
    }
    return copied;
}

// Copy single file and track in manifest
function copyFileWithManifest(src, dest, manifest, baseDir) {
    fs.copyFileSync(src, dest);
    
    const relPath = path.relative(baseDir, dest);
    const hash = getFileHash(dest);
    const stats = fs.statSync(dest);
    
    manifest.files[relPath] = {
        hash: hash,
        size: stats.size,
        type: path.extname(dest).slice(1) || 'unknown'
    };
}

function removeDir(dir) {
    if (!fs.existsSync(dir)) return 0;
    let removed = 0;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            removed += removeDir(fullPath);
            fs.rmdirSync(fullPath);
        } else {
            fs.unlinkSync(fullPath);
            removed++;
        }
    }
    return removed;
}

function getInstalledVersion(targetDir) {
    const versionFile = path.join(targetDir, '.droidpartment-version');
    if (fs.existsSync(versionFile)) {
        return fs.readFileSync(versionFile, 'utf8').trim();
    }
    // Check if droids exist but no version file (legacy install)
    const droidsDir = path.join(targetDir, 'droids');
    if (fs.existsSync(droidsDir) && fs.existsSync(path.join(droidsDir, 'dpt-memory.md'))) {
        return 'legacy';
    }
    return null;
}

function saveVersion(targetDir, version) {
    const versionFile = path.join(targetDir, '.droidpartment-version');
    fs.writeFileSync(versionFile, version);
}

function getFileSize(filePath) {
    if (!fs.existsSync(filePath)) return 0;
    return fs.statSync(filePath).size;
}

function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function countYamlEntries(filePath) {
    if (!fs.existsSync(filePath)) return 0;
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        // Match "- id:" with optional leading whitespace
        const matches = content.match(/^\s*- id:/gm);
        return matches ? matches.length : 0;
    } catch {
        return 0;
    }
}

function getProjectMemories(memoryDir) {
    const projectsDir = path.join(memoryDir, 'projects');
    if (!fs.existsSync(projectsDir)) return [];
    
    const projects = [];
    const entries = fs.readdirSync(projectsDir, { withFileTypes: true });
    
    for (const entry of entries) {
        if (entry.isDirectory()) {
            const projectPath = path.join(projectsDir, entry.name);
            const lessons = countYamlEntries(path.join(projectPath, 'lessons.yaml'));
            const mistakes = countYamlEntries(path.join(projectPath, 'mistakes.yaml'));
            const patterns = countYamlEntries(path.join(projectPath, 'patterns.yaml'));
            const size = getFileSize(path.join(projectPath, 'lessons.yaml')) +
                        getFileSize(path.join(projectPath, 'mistakes.yaml')) +
                        getFileSize(path.join(projectPath, 'patterns.yaml')) +
                        getFileSize(path.join(projectPath, 'sessions.json')) +
                        getFileSize(path.join(projectPath, 'STRUCTURE.md'));
            
            // Count sessions
            let sessions = 0;
            const sessionsFile = path.join(projectPath, 'sessions.json');
            if (fs.existsSync(sessionsFile)) {
                try {
                    const sessionsData = JSON.parse(fs.readFileSync(sessionsFile, 'utf8'));
                    sessions = (sessionsData.sessions || []).length;
                } catch {}
            }
            
            if (lessons > 0 || mistakes > 0 || patterns > 0 || sessions > 0 || size > 0) {
                projects.push({
                    name: entry.name,
                    lessons,
                    mistakes,
                    patterns,
                    sessions,
                    size
                });
            }
        }
    }
    return projects;
}

async function manageMemory(targetDir) {
    // Check if installed
    if (!isInstalled(targetDir)) {
        log.header('NOT INSTALLED');
        log.warn('Droidpartment is not installed yet.');
        log.info('Run: npx droidpartment');
        return;
    }
    
    const memoryDir = path.join(targetDir, 'memory');
    
    if (!fs.existsSync(memoryDir)) {
        log.warn('No memory directory found. Memory system not initialized.');
        return;
    }
    
    log.header('MEMORY MANAGEMENT');
    
    // Get memory stats
    const lessonsFile = path.join(memoryDir, 'lessons.yaml');
    const patternsFile = path.join(memoryDir, 'patterns.yaml');
    const mistakesFile = path.join(memoryDir, 'mistakes.yaml');
    const lessonsCount = countYamlEntries(lessonsFile);
    const patternsCount = countYamlEntries(patternsFile);
    const mistakesCount = countYamlEntries(mistakesFile);
    const lessonsSize = getFileSize(lessonsFile);
    const patternsSize = getFileSize(patternsFile);
    const mistakesSize = getFileSize(mistakesFile);
    const projects = getProjectMemories(memoryDir);
    
    // Display current status
    console.log(`${COLORS.bright}GLOBAL MEMORY:${COLORS.reset}`);
    console.log(`  Lessons:  ${lessonsCount} entries (${formatSize(lessonsSize)})`);
    console.log(`  Patterns: ${patternsCount} entries (${formatSize(patternsSize)})`);
    console.log(`  Mistakes: ${mistakesCount} entries (${formatSize(mistakesSize)})`);
    console.log('');
    
    console.log(`${COLORS.bright}PROJECT MEMORIES:${COLORS.reset}`);
    if (projects.length === 0) {
        console.log('  (none yet)');
    } else {
        for (const proj of projects) {
            const stats = [];
            if (proj.lessons > 0) stats.push(`${proj.lessons} lessons`);
            if (proj.mistakes > 0) stats.push(`${proj.mistakes} mistakes`);
            if (proj.patterns > 0) stats.push(`${proj.patterns} patterns`);
            if (proj.sessions > 0) stats.push(`${proj.sessions} sessions`);
            const statsStr = stats.length > 0 ? stats.join(', ') : 'empty';
            console.log(`  ${COLORS.cyan}${proj.name}${COLORS.reset}: ${statsStr} (${formatSize(proj.size)})`);
        }
    }
    console.log('');
    
    // Menu
    console.log('What would you like to clean?');
    console.log('');
    console.log(`  ${COLORS.green}1${COLORS.reset}) Exit (keep all)`);
    console.log(`  ${COLORS.yellow}2${COLORS.reset}) Clear global lessons`);
    console.log(`  ${COLORS.yellow}3${COLORS.reset}) Clear global patterns`);
    console.log(`  ${COLORS.yellow}4${COLORS.reset}) Clear global mistakes`);
    console.log(`  ${COLORS.yellow}5${COLORS.reset}) Clear specific project memory`);
    console.log(`  ${COLORS.red}6${COLORS.reset}) Clear ALL global memory`);
    console.log(`  ${COLORS.red}7${COLORS.reset}) Clear ALL project memories`);
    console.log(`  ${COLORS.red}8${COLORS.reset}) Clear EVERYTHING (start fresh)`);
    console.log('');
    
    const choice = await prompt('Select option [1-8]', '1');
    
    switch (choice) {
        case '1':
            log.info('No changes made.');
            break;
            
        case '2':
            if (fs.existsSync(lessonsFile)) {
                fs.writeFileSync(lessonsFile, `# GLOBAL LESSONS - Universal Knowledge\nlessons: []\n`);
                log.success(`Cleared ${lessonsCount} lessons`);
            }
            break;
            
        case '3':
            if (fs.existsSync(patternsFile)) {
                fs.writeFileSync(patternsFile, `# GLOBAL PATTERNS - Universal Truths\npatterns: []\n`);
                log.success(`Cleared ${patternsCount} patterns`);
            }
            break;
            
        case '4':
            if (fs.existsSync(mistakesFile)) {
                fs.writeFileSync(mistakesFile, `# GLOBAL MISTAKES - Prevention Database\nmistakes: []\n`);
                log.success(`Cleared ${mistakesCount} mistakes`);
            }
            break;
            
        case '5':
            if (projects.length === 0) {
                log.warn('No project memories to clear.');
            } else {
                console.log('');
                console.log('Which project memory to clear?');
                console.log('');
                projects.forEach((proj, i) => {
                    console.log(`  ${COLORS.yellow}${i + 1}${COLORS.reset}) ${proj.name} (${proj.lessons} lessons, ${proj.mistakes} mistakes)`);
                });
                console.log(`  ${COLORS.green}0${COLORS.reset}) Cancel`);
                console.log('');
                
                const projChoice = await prompt('Select project', '0');
                const projIndex = parseInt(projChoice) - 1;
                
                if (projIndex >= 0 && projIndex < projects.length) {
                    const projDir = path.join(memoryDir, 'projects', projects[projIndex].name);
                    removeDir(projDir);
                    fs.rmdirSync(projDir);
                    log.success(`Cleared memory for: ${projects[projIndex].name}`);
                } else {
                    log.info('Cancelled.');
                }
            }
            break;
            
        case '6':
            if (fs.existsSync(lessonsFile)) {
                fs.writeFileSync(lessonsFile, `# GLOBAL LESSONS - Universal Knowledge\nlessons: []\n`);
            }
            if (fs.existsSync(patternsFile)) {
                fs.writeFileSync(patternsFile, `# GLOBAL PATTERNS - Universal Truths\npatterns: []\n`);
            }
            if (fs.existsSync(mistakesFile)) {
                fs.writeFileSync(mistakesFile, `# GLOBAL MISTAKES - Prevention Database\nmistakes: []\n`);
            }
            log.success(`Cleared all global memory (${lessonsCount} lessons, ${patternsCount} patterns, ${mistakesCount} mistakes)`);
            break;
            
        case '7':
            if (projects.length === 0) {
                log.warn('No project memories to clear.');
            } else {
                const projectsDir = path.join(memoryDir, 'projects');
                for (const proj of projects) {
                    const projDir = path.join(projectsDir, proj.name);
                    removeDir(projDir);
                    fs.rmdirSync(projDir);
                }
                log.success(`Cleared ${projects.length} project memories`);
            }
            break;
            
        case '8':
            // Clear global
            if (fs.existsSync(lessonsFile)) {
                fs.writeFileSync(lessonsFile, `# GLOBAL LESSONS - Universal Knowledge\nlessons: []\n`);
            }
            if (fs.existsSync(patternsFile)) {
                fs.writeFileSync(patternsFile, `# GLOBAL PATTERNS - Universal Truths\npatterns: []\n`);
            }
            if (fs.existsSync(mistakesFile)) {
                fs.writeFileSync(mistakesFile, `# GLOBAL MISTAKES - Prevention Database\nmistakes: []\n`);
            }
            // Clear projects
            if (projects.length > 0) {
                const projectsDir = path.join(memoryDir, 'projects');
                for (const proj of projects) {
                    const projDir = path.join(projectsDir, proj.name);
                    removeDir(projDir);
                    fs.rmdirSync(projDir);
                }
            }
            log.success('Cleared ALL memory - starting fresh like a newborn!');
            break;
            
        default:
            log.info('Invalid choice. No changes made.');
    }
}

function compareVersions(v1, v2) {
    if (v1 === 'legacy') return -1;
    if (v2 === 'legacy') return 1;
    
    const parts1 = v1.split('.').map(Number);
    const parts2 = v2.split('.').map(Number);
    
    for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
        const p1 = parts1[i] || 0;
        const p2 = parts2[i] || 0;
        if (p1 > p2) return 1;
        if (p1 < p2) return -1;
    }
    return 0;
}

function isInstalled(targetDir) {
    const versionFile = path.join(targetDir, '.droidpartment-version');
    const chiefFile = path.join(targetDir, 'droids', 'dpt-chief.md');
    return fs.existsSync(versionFile) || fs.existsSync(chiefFile);
}

async function uninstall(targetDir, autoYes = false, purgeMemory = false) {
    // Check if installed
    if (!isInstalled(targetDir)) {
        log.header('NOTHING TO UNINSTALL');
        log.info(`Droidpartment is not installed in ${targetDir}`);
        log.success('Already clean!');
        return;
    }
    
    log.header('UNINSTALLING DROIDPARTMENT');
    
    let totalRemoved = 0;
    
    // Load manifest for clean uninstall
    const manifest = loadManifest(targetDir);
    
    if (manifest && manifest.files) {
        // === MANIFEST-BASED UNINSTALL (CLEAN) ===
        log.info('Using manifest for clean uninstall...');
        
        // Files to PRESERVE (user's learning data) - never delete these
        const preserveFiles = [
            'memory/lessons.yaml',
            'memory/mistakes.yaml', 
            'memory/patterns.yaml',
            'memory/stats.yaml'
        ];
        
        // Remove all tracked files EXCEPT learning data
        const files = Object.keys(manifest.files);
        let preserved = 0;
        for (const relPath of files) {
            // Skip learning files - preserve user data
            if (preserveFiles.some(p => relPath.endsWith(p.replace('memory/', '')))) {
                log.verbose(`Preserved: ${relPath} (learning data)`);
                preserved++;
                continue;
            }
            
            const fullPath = path.join(targetDir, relPath);
            if (fs.existsSync(fullPath)) {
                try {
                    fs.unlinkSync(fullPath);
                    log.verbose(`Removed: ${relPath}`);
                    totalRemoved++;
                } catch (e) {
                    log.warn(`Could not remove: ${relPath}`);
                }
            }
        }
        log.success(`Removed ${totalRemoved} tracked files`);
        if (preserved > 0) {
            log.info(`Preserved ${preserved} learning files (lessons, mistakes, patterns)`);
        }
        
        // Remove tracked directories (in reverse order - deepest first)
        const dirs = [...(manifest.directories || [])].sort((a, b) => b.length - a.length);
        let dirsRemoved = 0;
        for (const relDir of dirs) {
            const fullDir = path.join(targetDir, relDir);
            if (fs.existsSync(fullDir)) {
                try {
                    const remaining = fs.readdirSync(fullDir);
                    // Only remove if empty or only contains __pycache__
                    if (remaining.length === 0 || 
                        (remaining.length === 1 && remaining[0] === '__pycache__')) {
                        if (remaining.includes('__pycache__')) {
                            removeDir(path.join(fullDir, '__pycache__'));
                            fs.rmdirSync(path.join(fullDir, '__pycache__'));
                        }
                        fs.rmdirSync(fullDir);
                        dirsRemoved++;
                    }
                } catch (e) { /* ignore - not empty */ }
            }
        }
        if (dirsRemoved > 0) {
            log.success(`Removed ${dirsRemoved} directories`);
        }
    } else {
        // No manifest found - cannot uninstall cleanly
        log.error('No manifest found. Cannot determine installed files.');
        log.error('Please reinstall Droidpartment first, then uninstall.');
        return;
    }
    
    // Remove hook registrations from Factory settings
    const settingsPath = path.join(process.env.HOME || process.env.USERPROFILE, '.factory', 'settings.json');
    try {
        if (fs.existsSync(settingsPath)) {
            let content = fs.readFileSync(settingsPath, 'utf8');
            content = content.replace(/\/\/.*$/gm, '');
            content = content.replace(/\/\*[\s\S]*?\*\//g, '');
            const settings = JSON.parse(content);
            
            if (settings.hooks) {
                delete settings.hooks.SessionStart;
                delete settings.hooks.SubagentStop;
                delete settings.hooks.PostToolUse;
                delete settings.hooks.SessionEnd;
                delete settings.hooks.PreToolUse;
                delete settings.hooks.UserPromptSubmit;
                
                if (Object.keys(settings.hooks).length === 0) {
                    delete settings.hooks;
                }
                
                fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
                log.success('Removed hook registrations from Factory settings');
            }
        }
    } catch (e) {
        log.warn('Could not remove hook registrations: ' + e.message);
    }
    
    // Handle memory directory
    const memoryDir = path.join(targetDir, 'memory');
    if (fs.existsSync(memoryDir)) {
        // Count memory data (YAML files only - these are the learning data)
        const lessonsFile = path.join(memoryDir, 'lessons.yaml');
        const patternsFile = path.join(memoryDir, 'patterns.yaml');
        const mistakesFile = path.join(memoryDir, 'mistakes.yaml');
        const lessonsCount = countYamlEntries(lessonsFile);
        const patternsCount = countYamlEntries(patternsFile);
        const mistakesCount = countYamlEntries(mistakesFile);
        const totalMemory = lessonsCount + patternsCount + mistakesCount;
        
        // Always remove: hooks/, *.py, *.json (these are code/state, not user data)
        const hooksDir = path.join(memoryDir, 'hooks');
        if (fs.existsSync(hooksDir)) {
            const hooksRemoved = removeDir(hooksDir);
            try { fs.rmdirSync(hooksDir); } catch (e) { /* ignore */ }
            log.success(`Removed hooks (${hooksRemoved} files)`);
            totalRemoved += hooksRemoved;
        }
        
        // Remove ALL .py files (Python modules)
        const pyFiles = fs.readdirSync(memoryDir).filter(f => f.endsWith('.py'));
        for (const pyFile of pyFiles) {
            fs.unlinkSync(path.join(memoryDir, pyFile));
            totalRemoved++;
        }
        if (pyFiles.length > 0) {
            log.success(`Removed ${pyFiles.length} Python modules`);
        }
        
        // Remove ALL .json files (state files, not user data)
        const jsonFiles = fs.readdirSync(memoryDir).filter(f => f.endsWith('.json'));
        for (const jsonFile of jsonFiles) {
            fs.unlinkSync(path.join(memoryDir, jsonFile));
            totalRemoved++;
        }
        if (jsonFiles.length > 0) {
            log.success(`Removed ${jsonFiles.length} state files`);
        }
        
        // Remove __pycache__ if exists
        const pycacheDir = path.join(memoryDir, '__pycache__');
        if (fs.existsSync(pycacheDir)) {
            removeDir(pycacheDir);
            try { fs.rmdirSync(pycacheDir); } catch (e) { /* ignore */ }
            log.success('Removed __pycache__');
        }
        
        // Handle YAML memory files (user learning data)
        if (totalMemory > 0) {
            log.warn(`Memory found: ${lessonsCount} lessons, ${patternsCount} patterns, ${mistakesCount} mistakes`);
            
            let deleteMemory = purgeMemory;
            
            if (!autoYes && !purgeMemory) {
                console.log('');
                console.log(`${COLORS.cyan}Preserve Memory Data?${COLORS.reset}`);
                console.log('');
                console.log(`  ${COLORS.green}1${COLORS.reset}) Keep memory (default)`);
                console.log('     Your learning is preserved for next reinstall');
                console.log('');
                console.log(`  ${COLORS.red}2${COLORS.reset}) Delete memory`);
                console.log('     Clean slate on next install');
                console.log('');
                
                const choice = await prompt('Select option [1/2]', '1');
                deleteMemory = choice === '2';
            }
            
            if (deleteMemory) {
                // Delete YAML memory files
                if (fs.existsSync(lessonsFile)) fs.unlinkSync(lessonsFile);
                if (fs.existsSync(patternsFile)) fs.unlinkSync(patternsFile);
                if (fs.existsSync(mistakesFile)) fs.unlinkSync(mistakesFile);
                const statsFile = path.join(memoryDir, 'stats.yaml');
                if (fs.existsSync(statsFile)) fs.unlinkSync(statsFile);
                
                // Remove projects directory
                const projectsDir = path.join(memoryDir, 'projects');
                if (fs.existsSync(projectsDir)) {
                    removeDir(projectsDir);
                    try { fs.rmdirSync(projectsDir); } catch (e) { /* ignore */ }
                }
                
                log.success(`Deleted memory (${lessonsCount} lessons, ${patternsCount} patterns, ${mistakesCount} mistakes)`);
                totalRemoved += 4;
                
                // Try to remove memory directory if empty
                try {
                    const remaining = fs.readdirSync(memoryDir);
                    if (remaining.length === 0) {
                        fs.rmdirSync(memoryDir);
                        log.success('Removed empty memory directory');
                    }
                } catch (e) { /* ignore */ }
            } else {
                // Preserve memory YAML files
                log.success(`Preserved memory (${lessonsCount} lessons, ${patternsCount} patterns, ${mistakesCount} mistakes)`);
                log.info('Memory will be available on next install');
            }
        } else {
            // No learning data - remove remaining files and directory
            const statsFile = path.join(memoryDir, 'stats.yaml');
            if (fs.existsSync(statsFile)) fs.unlinkSync(statsFile);
            
            // Remove projects directory if exists
            const projectsDir = path.join(memoryDir, 'projects');
            if (fs.existsSync(projectsDir)) {
                removeDir(projectsDir);
                try { fs.rmdirSync(projectsDir); } catch (e) { /* ignore */ }
            }
            
            // Try to remove memory directory if empty
            try {
                const remaining = fs.readdirSync(memoryDir);
                if (remaining.length === 0) {
                    fs.rmdirSync(memoryDir);
                    log.success('Removed empty memory directory');
                }
            } catch (e) { /* ignore */ }
        }
    }
    
    // Remove AGENTS.md
    const agentsMd = path.join(targetDir, 'AGENTS.md');
    if (fs.existsSync(agentsMd)) {
        fs.unlinkSync(agentsMd);
        log.success('Removed AGENTS.md');
        totalRemoved++;
    }
    
    // Remove manifest file
    const manifestPath = path.join(targetDir, MANIFEST_FILE);
    if (fs.existsSync(manifestPath)) {
        fs.unlinkSync(manifestPath);
        log.verbose('Removed manifest');
        totalRemoved++;
    }
    
    // Remove version file
    const versionFile = path.join(targetDir, '.droidpartment-version');
    if (fs.existsSync(versionFile)) {
        fs.unlinkSync(versionFile);
        totalRemoved++;
    }
    
    log.header('UNINSTALL COMPLETE');
    console.log(`Removed ${totalRemoved} items from ${targetDir}`);
    console.log('');
    log.info('Restart droid CLI to apply changes.');
}

function update(targetDir, installedVersion) {
    log.header('UPDATING DROIDPARTMENT');
    console.log(`${COLORS.yellow}Installed:${COLORS.reset} ${installedVersion}`);
    console.log(`${COLORS.green}Available:${COLORS.reset} ${CURRENT_VERSION}`);
    console.log('');
    
    // Load old manifest to detect stale files
    const oldManifest = loadManifest(targetDir);
    
    // Create new manifest
    const newManifest = createManifest(CURRENT_VERSION);
    if (oldManifest) {
        newManifest.installedAt = oldManifest.installedAt; // Preserve original install date
    }
    
    // Update droids with manifest tracking
    log.header('UPDATING AGENTS');
    const droidsSource = path.join(TEMPLATES_DIR, 'droids');
    const droidsTarget = path.join(targetDir, 'droids');
    ensureDir(droidsTarget);
    const droidsCopied = copyDirWithManifest(droidsSource, droidsTarget, newManifest, targetDir);
    log.success(`Updated ${droidsCopied} agent(s)`);
    
    // Update skills with manifest tracking
    const skillsSource = path.join(TEMPLATES_DIR, 'skills');
    const skillsTarget = path.join(targetDir, 'skills');
    if (fs.existsSync(skillsSource)) {
        ensureDir(skillsTarget);
        const skillsCopied = copyDirWithManifest(skillsSource, skillsTarget, newManifest, targetDir);
        log.success(`Updated ${skillsCopied} skill file(s)`);
    }
    
    // Update AGENTS.md with manifest tracking
    const agentsMdSource = path.join(TEMPLATES_DIR, 'AGENTS.md');
    if (fs.existsSync(agentsMdSource)) {
        const agentsMdTarget = path.join(targetDir, 'AGENTS.md');
        copyFileWithManifest(agentsMdSource, agentsMdTarget, newManifest, targetDir);
        log.success('Updated AGENTS.md orchestrator');
    }
    
    // Update hooks with manifest tracking
    log.header('UPDATING HOOKS');
    const hooksSource = path.join(TEMPLATES_DIR, 'hooks');
    const memoryTarget = path.join(targetDir, 'memory');
    const hooksTarget = path.join(memoryTarget, 'hooks');
    newManifest.directories.push('memory');
    newManifest.directories.push('memory/hooks');
    
    if (fs.existsSync(hooksSource)) {
        ensureDir(hooksTarget);
        const hooksCopied = copyDirWithManifest(hooksSource, hooksTarget, newManifest, targetDir);
        log.success(`Updated ${hooksCopied} hooks`);
        
        // Re-register hooks in Factory settings
        registerHooks(hooksTarget);
    }
    
    // Update Python modules with manifest tracking
    log.header('UPDATING PYTHON MODULES');
    const memorySource = path.join(TEMPLATES_DIR, 'memory');
    const pythonModules = ['context_index.py', 'workflow_state.py', 'shared_context.py'];
    let modulesUpdated = 0;
    for (const module of pythonModules) {
        const srcPath = path.join(memorySource, module);
        const destPath = path.join(memoryTarget, module);
        if (fs.existsSync(srcPath)) {
            copyFileWithManifest(srcPath, destPath, newManifest, targetDir);
            modulesUpdated++;
        }
    }
    if (modulesUpdated > 0) {
        log.success(`Updated ${modulesUpdated} Python modules`);
    }
    
    // === STALE FILE CLEANUP ===
    // Remove files that were in old manifest but NOT in new manifest
    if (oldManifest && oldManifest.files) {
        const oldFiles = new Set(Object.keys(oldManifest.files));
        const newFiles = new Set(Object.keys(newManifest.files));
        
        let staleRemoved = 0;
        for (const oldFile of oldFiles) {
            if (!newFiles.has(oldFile)) {
                const fullPath = path.join(targetDir, oldFile);
                if (fs.existsSync(fullPath)) {
                    try {
                        fs.unlinkSync(fullPath);
                        log.verbose(`Removed stale: ${oldFile}`);
                        staleRemoved++;
                    } catch (e) { /* ignore */ }
                }
            }
        }
        if (staleRemoved > 0) {
            log.success(`Removed ${staleRemoved} stale files from old version`);
        }
    }
    
    // NOTE: We don't update memory YAML files to preserve learned data!
    log.info('Memory data preserved (lessons, patterns, mistakes kept)');
    
    // Save new manifest
    newManifest.settingsModified = true;
    newManifest.hooksRegistered = ['SessionStart', 'SubagentStop', 'PostToolUse', 'SessionEnd', 'PreToolUse', 'UserPromptSubmit'];
    saveManifest(targetDir, newManifest);
    log.success(`Manifest updated (${Object.keys(newManifest.files).length} files tracked)`);
    
    // Save new version
    saveVersion(targetDir, CURRENT_VERSION);
    
    log.header('UPDATE COMPLETE');
    console.log(`${COLORS.bright}Updated to:${COLORS.reset} v${CURRENT_VERSION}`);
    console.log('');
    log.info('Restart droid CLI to apply changes.');
}

function registerHooks(hooksTarget) {
    const settingsDir = path.join(process.env.HOME || process.env.USERPROFILE, '.factory');
    const settingsPath = path.join(settingsDir, 'settings.json');
    ensureDir(settingsDir);

    let settings = {};
    try {
        if (fs.existsSync(settingsPath)) {
            let content = fs.readFileSync(settingsPath, 'utf8');
            content = content.replace(/\/\/.*$/gm, '');
            content = content.replace(/\/\*[\s\S]*?\*\//g, '');
            settings = JSON.parse(content);
        }
    } catch (e) {
        settings = {};
    }

    if (!settings.hooks) {
        settings.hooks = {};
    }

    const hooksPathForward = hooksTarget.replace(/\\/g, '/');
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    settings.hooks.SessionStart = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-session-start.py`, "timeout": 30}]
    }];
    settings.hooks.SubagentStop = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-subagent-stop.py`, "timeout": 15}]
    }];
    settings.hooks.PostToolUse = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-post-tool-use.py`, "timeout": 10}]
    }];
    settings.hooks.SessionEnd = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-session-end.py`, "timeout": 30}]
    }];
    settings.hooks.PreToolUse = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-pre-tool-use.py`, "timeout": 10}]
    }];
    settings.hooks.UserPromptSubmit = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-user-prompt-submit.py`, "timeout": 15}]
    }];

    try {
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
        log.success('Hooks registered in Factory settings');
    } catch (e) {
        log.warn('Could not register hooks: ' + e.message);
    }
}

async function prompt(question, defaultValue = '') {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        const defaultText = defaultValue ? ` (${defaultValue})` : '';
        rl.question(`${question}${defaultText}: `, (answer) => {
            rl.close();
            resolve(answer || defaultValue);
        });
    });
}

function showBanner() {
    console.log(`
${COLORS.bright}${COLORS.cyan}
  ____  ____   ___  ___ ____  ____   _    ____ _____ __  __ _____ _   _ _____ 
 |  _ \\|  _ \\ / _ \\|_ _|  _ \\|  _ \\ / \\  |  _ \\_   _|  \\/  | ____| \\ | |_   _|
 | | | | |_) | | | || || | | | |_) / _ \\ | |_) || | | |\\/| |  _| |  \\| | | |  
 | |_| |  _ <| |_| || || |_| |  __/ ___ \\|  _ < | | | |  | | |___| |\\  | | |  
 |____/|_| \\_\\\\___/|___|____/|_| /_/   \\_\\_| \\_\\|_| |_|  |_|_____|_| \_| |_|  
                                                                              
${COLORS.reset}
           ${COLORS.bright}Autonomous Software Development Department${COLORS.reset}
                      ${COLORS.cyan}18 Expert Agents (dpt-*)${COLORS.reset}
                              ${COLORS.yellow}v${CURRENT_VERSION}${COLORS.reset}
`);
}

function install(targetDir) {
    // Create manifest to track all installed files
    const manifest = createManifest(CURRENT_VERSION);
    
    // Create directories
    const droidsTarget = path.join(targetDir, 'droids');
    const skillsTarget = path.join(targetDir, 'skills');
    
    ensureDir(droidsTarget);
    ensureDir(skillsTarget);
    
    // Copy droids with manifest tracking
    log.header('INSTALLING AGENTS');
    const droidsSource = path.join(TEMPLATES_DIR, 'droids');
    const droidsCopied = copyDirWithManifest(droidsSource, droidsTarget, manifest, targetDir);
    log.success(`Installed ${droidsCopied} agent(s)`);
    
    // Copy skills with manifest tracking
    const skillsSource = path.join(TEMPLATES_DIR, 'skills');
    if (fs.existsSync(skillsSource)) {
        const skillsCopied = copyDirWithManifest(skillsSource, skillsTarget, manifest, targetDir);
        log.success(`Installed ${skillsCopied} skill file(s)`);
    }
    
    // Copy memory system with manifest tracking
    log.header('INSTALLING MEMORY SYSTEM');
    const memoryTarget = path.join(targetDir, 'memory');
    const memorySource = path.join(TEMPLATES_DIR, 'memory');
    ensureDir(memoryTarget);
    ensureDir(path.join(memoryTarget, 'projects')); // For per-project memories
    manifest.directories.push('memory');
    manifest.directories.push('memory/projects');
    
    if (fs.existsSync(memorySource)) {
        const memoryCopied = copyDirWithManifest(memorySource, memoryTarget, manifest, targetDir);
        log.success(`Installed global memory (${memoryCopied} files)`);
        log.info('Global: lessons.yaml, patterns.yaml, mistakes.yaml (shared across all projects)');
        log.info('Per-project: memory/projects/{project}/ (auto-created when needed)');
    }
    
    // Copy hooks with manifest tracking
    log.header('INSTALLING FACTORY HOOKS');
    const hooksSource = path.join(TEMPLATES_DIR, 'hooks');
    const hooksTarget = path.join(memoryTarget, 'hooks');
    if (fs.existsSync(hooksSource)) {
        ensureDir(hooksTarget);
        const hooksCopied = copyDirWithManifest(hooksSource, hooksTarget, manifest, targetDir);
        log.success(`Installed ${hooksCopied} Factory hooks`);
        log.info('Hooks enable automatic:');
        log.info('  ✓ Memory initialization (SessionStart)');
        log.info('  ✓ Context transfer between agents (SubagentStop)');
        log.info('  ✓ Progress tracking (PostToolUse)');
        log.info('  ✓ Session cleanup (SessionEnd)');
        log.info('  ✓ Tool validation (PreToolUse)');
        log.info('  ✓ Prompt enrichment (UserPromptSubmit)');
    }
    
    // Register hooks in Factory settings (handles JSONC format)
    const settingsDir = path.join(process.env.HOME || process.env.USERPROFILE, '.factory');
    const settingsPath = path.join(settingsDir, 'settings.json');
    ensureDir(settingsDir);

    let settings = {};
    try {
        if (fs.existsSync(settingsPath)) {
            // Read and strip JSONC comments (// and /* */)
            let content = fs.readFileSync(settingsPath, 'utf8');
            content = content.replace(/\/\/.*$/gm, ''); // Remove // comments
            content = content.replace(/\/\*[\s\S]*?\*\//g, ''); // Remove /* */ comments
            settings = JSON.parse(content);
        }
    } catch (e) {
        log.warn('Could not parse settings.json, creating fresh hooks config');
        settings = {};
    }

    if (!settings.hooks) {
        settings.hooks = {};
    }

    // Use forward slashes for cross-platform compatibility
    const hooksPathForward = hooksTarget.replace(/\\/g, '/');
    
    // Detect Python command (python on Windows, python3 on Unix)
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    // Register 6 hooks with proper paths and timeouts (per Factory AI specification)
    settings.hooks.SessionStart = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-session-start.py`, "timeout": 30}]
    }];
    settings.hooks.SubagentStop = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-subagent-stop.py`, "timeout": 15}]
    }];
    settings.hooks.PostToolUse = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-post-tool-use.py`, "timeout": 10}]
    }];
    settings.hooks.SessionEnd = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-session-end.py`, "timeout": 30}]
    }];
    settings.hooks.PreToolUse = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-pre-tool-use.py`, "timeout": 10}]
    }];
    settings.hooks.UserPromptSubmit = [{
        "matcher": "*",
        "hooks": [{"type": "command", "command": `${pythonCmd} ${hooksPathForward}/hook-user-prompt-submit.py`, "timeout": 15}]
    }];

    try {
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
        log.success('Hooks registered in Factory settings');
        log.info(`  Using: ${pythonCmd} with forward-slash paths`);
    } catch (e) {
        log.warn('Could not register hooks: ' + e.message);
    }
    
    // Copy AGENTS.md with manifest tracking
    const agentsMdSource = path.join(TEMPLATES_DIR, 'AGENTS.md');
    if (fs.existsSync(agentsMdSource)) {
        const agentsMdTarget = path.join(targetDir, 'AGENTS.md');
        copyFileWithManifest(agentsMdSource, agentsMdTarget, manifest, targetDir);
        log.success('Installed AGENTS.md orchestrator');
    }
    
    // Mark settings as modified and track hooks
    manifest.settingsModified = true;
    manifest.hooksRegistered = ['SessionStart', 'SubagentStop', 'PostToolUse', 'SessionEnd', 'PreToolUse', 'UserPromptSubmit'];
    
    // Save manifest (THIS IS THE KEY - tracks everything we installed)
    saveManifest(targetDir, manifest);
    log.success(`Manifest saved (${Object.keys(manifest.files).length} files tracked)`);
    
    // Save version (legacy compatibility)
    saveVersion(targetDir, CURRENT_VERSION);

    // Summary
    log.header('INSTALLATION COMPLETE');
    
    console.log(`${COLORS.bright}Installed:${COLORS.reset} v${CURRENT_VERSION}`);
    console.log(`${COLORS.bright}Location:${COLORS.reset} ${targetDir}`);
    console.log('');
    
    log.header('NEXT STEPS');
    console.log('1. Enable Custom Droids in Factory:');
    console.log('   /settings → Experimental → Custom Droids');
    console.log('');
    console.log('2. Restart droid CLI');
    console.log('');
    console.log('3. Just describe your task - agents work automatically!');
    console.log('');
    console.log(`${COLORS.bright}Commands:${COLORS.reset}`);
    console.log('   npx droidpartment              # Check for updates');
    console.log('   npx droidpartment --memory     # Manage/clean memory');
    console.log('   npx droidpartment --uninstall  # Remove');
    console.log('');
    
    log.success('Droidpartment is ready!');
}

function showAgentList() {
    console.log(`${COLORS.bright}18 Expert Agents (called via Task tool):${COLORS.reset}`);
    console.log('');
    console.log('  Memory & Output (SEQUENTIAL - must wait):');
    console.log('  • dpt-memory     - Learning system (START/END of tasks)');
    console.log('  • dpt-output     - Format results with memory stats');
    console.log('');
    console.log('  Planning (SEQUENTIAL):');
    console.log('  • dpt-product    - Requirements, user stories');
    console.log('  • dpt-research   - Best practices from official docs');
    console.log('  • dpt-arch       - Architecture, ADRs, patterns');
    console.log('  • dpt-scrum      - Task breakdown, dependencies');
    console.log('');
    console.log('  Implementation:');
    console.log('  • dpt-dev        - Code implementation');
    console.log('  • dpt-data       - Database, queries, indexes');
    console.log('  • dpt-api        - API design, REST');
    console.log('  • dpt-ux         - UI/UX, accessibility');
    console.log('  • dpt-ops        - DevOps, CI/CD');
    console.log('');
    console.log('  Quality (CAN BE PARALLEL):');
    console.log('  • dpt-sec        - Security (OWASP, CWE)');
    console.log('  • dpt-lead       - Code review (SOLID)');
    console.log('  • dpt-qa         - Testing (pyramid)');
    console.log('  • dpt-review     - Simplicity check');
    console.log('  • dpt-perf       - Performance (measure first!)');
    console.log('');
    console.log('  Support:');
    console.log('  • dpt-docs       - Documentation');
    console.log('  • dpt-grammar    - Grammar, clarity');
    console.log('');
    console.log('  Memory System:');
    console.log('  • GLOBAL: lessons, patterns, mistakes (all projects)');
    console.log('  • PER-PROJECT: knowledge per project');
    console.log('  • Learning curve tracked over time');
    console.log('');
}

function showHelp() {
    console.log(`
${COLORS.bright}Droidpartment${COLORS.reset} v${CURRENT_VERSION} - 18 Expert AI Agents for Factory AI

${COLORS.bright}USAGE:${COLORS.reset}
  npx droidpartment [command] [options]

${COLORS.bright}COMMANDS:${COLORS.reset}
  ${COLORS.green}(none)${COLORS.reset}          Interactive install/update (default)
  ${COLORS.green}install${COLORS.reset}         Install Droidpartment
  ${COLORS.green}update${COLORS.reset}          Update to latest version
  ${COLORS.green}reinstall${COLORS.reset}       Fresh install (uninstall + install)
  ${COLORS.yellow}status${COLORS.reset}          Check installation status
  ${COLORS.yellow}stats${COLORS.reset}           Show usage & learning statistics
  ${COLORS.yellow}memory${COLORS.reset}          Manage/clean memory files
  ${COLORS.red}uninstall${COLORS.reset}       Remove Droidpartment

${COLORS.bright}OPTIONS:${COLORS.reset}
  ${COLORS.cyan}-y, --yes${COLORS.reset}       Auto-confirm all prompts
  ${COLORS.cyan}-q, --quiet${COLORS.reset}     Minimal output (errors only)
  ${COLORS.cyan}-v, --verbose${COLORS.reset}   Detailed output
  ${COLORS.cyan}--project${COLORS.reset}       Install to ./.factory (project-level)
  ${COLORS.cyan}--force${COLORS.reset}         Force operation even if unnecessary
  ${COLORS.cyan}--dry-run${COLORS.reset}       Preview changes without applying
  ${COLORS.cyan}--purge${COLORS.reset}         Delete memory during uninstall
  ${COLORS.cyan}--version${COLORS.reset}       Show version number
  ${COLORS.cyan}--help${COLORS.reset}          Show this help message

${COLORS.bright}EXAMPLES:${COLORS.reset}
  npx droidpartment                    # Interactive install
  npx droidpartment install -y         # Auto-install
  npx droidpartment update             # Update to latest
  npx droidpartment status             # Check status
  npx droidpartment stats              # View usage statistics
  npx droidpartment reinstall --force  # Force fresh install
  npx droidpartment uninstall --purge  # Remove + delete memory
  npx droidpartment memory             # Manage memory
  npx droidpartment install --dry-run  # Preview install

${COLORS.bright}MORE INFO:${COLORS.reset}
  https://github.com/UntaDotMy/Droidpartment
`);
}

function checkInstallation() {
    log.header('INSTALLATION CHECK');
    
    const personalInstalled = getInstalledVersion(PERSONAL_DIR);
    const projectInstalled = getInstalledVersion(PROJECT_DIR);
    
    console.log(`${COLORS.bright}Personal (~/.factory):${COLORS.reset}`);
    if (personalInstalled) {
        log.success(`Installed v${personalInstalled}`);
        
        // Check components
        const droidsDir = path.join(PERSONAL_DIR, 'droids');
        const memoryDir = path.join(PERSONAL_DIR, 'memory');
        const hooksDir = path.join(memoryDir, 'hooks');
        const agentsMd = path.join(PERSONAL_DIR, 'AGENTS.md');
        
        const droidsCount = fs.existsSync(droidsDir) ? fs.readdirSync(droidsDir).filter(f => f.endsWith('.md')).length : 0;
        const hooksCount = fs.existsSync(hooksDir) ? fs.readdirSync(hooksDir).filter(f => f.endsWith('.py')).length : 0;
        const hasAgentsMd = fs.existsSync(agentsMd);
        const hasMemory = fs.existsSync(memoryDir);
        
        console.log(`  Agents: ${droidsCount}/18`);
        console.log(`  Hooks: ${hooksCount}/4`);
        console.log(`  AGENTS.md: ${hasAgentsMd ? 'yes' : 'missing'}`);
        console.log(`  Memory: ${hasMemory ? 'yes' : 'not initialized'}`);
        
        // Check memory stats
        if (hasMemory) {
            const lessonsCount = countYamlEntries(path.join(memoryDir, 'lessons.yaml'));
            const patternsCount = countYamlEntries(path.join(memoryDir, 'patterns.yaml'));
            const mistakesCount = countYamlEntries(path.join(memoryDir, 'mistakes.yaml'));
            console.log(`  Learning: ${lessonsCount} lessons, ${patternsCount} patterns, ${mistakesCount} mistakes`);
            
            // Check droid usage stats
            const droidUsageFile = path.join(memoryDir, 'droid_usage.json');
            if (fs.existsSync(droidUsageFile)) {
                try {
                    const droidStats = JSON.parse(fs.readFileSync(droidUsageFile, 'utf8'));
                    const totalCalls = droidStats.total_calls || 0;
                    const topDroids = Object.entries(droidStats.droids || {})
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 3)
                        .map(([name, count]) => `${name}(${count})`)
                        .join(', ');
                    console.log(`  Droid Calls: ${totalCalls} total${topDroids ? ` (top: ${topDroids})` : ''}`);
                } catch {}
            }
            
            // Check tool usage stats
            const toolStatsFile = path.join(memoryDir, 'tool_stats.json');
            if (fs.existsSync(toolStatsFile)) {
                try {
                    const toolStats = JSON.parse(fs.readFileSync(toolStatsFile, 'utf8'));
                    const totalExec = toolStats.total_executions || 0;
                    const errors = toolStats.errors || 0;
                    console.log(`  Tool Calls: ${totalExec} total, ${errors} errors`);
                } catch {}
            }
            
            // Check session stats
            const sessionHistoryFile = path.join(memoryDir, 'session_history.json');
            if (fs.existsSync(sessionHistoryFile)) {
                try {
                    const history = JSON.parse(fs.readFileSync(sessionHistoryFile, 'utf8'));
                    const sessionCount = (history.sessions || []).length;
                    console.log(`  Sessions: ${sessionCount} recorded`);
                } catch {}
            }
            
            // Check project count
            const projects = getProjectMemories(memoryDir);
            if (projects.length > 0) {
                const totalProjectLessons = projects.reduce((sum, p) => sum + p.lessons, 0);
                const totalProjectSessions = projects.reduce((sum, p) => sum + p.sessions, 0);
                console.log(`  Projects: ${projects.length} indexed (${totalProjectLessons} lessons, ${totalProjectSessions} sessions)`);
            }
        }
        
        // Check if update available
        if (compareVersions(CURRENT_VERSION, personalInstalled) > 0) {
            log.warn(`Update available: v${CURRENT_VERSION}`);
        }
    } else {
        log.info('Not installed');
    }
    
    console.log('');
    console.log(`${COLORS.bright}Project (./.factory):${COLORS.reset}`);
    if (projectInstalled) {
        log.success(`Installed v${projectInstalled}`);
    } else {
        log.info('Not installed');
    }
    
    console.log('');
    console.log(`${COLORS.bright}Available Version:${COLORS.reset} v${CURRENT_VERSION}`);
    
    // Check Factory settings
    const settingsPath = path.join(PERSONAL_DIR, 'settings.json');
    if (fs.existsSync(settingsPath)) {
        try {
            let content = fs.readFileSync(settingsPath, 'utf8');
            content = content.replace(/\/\/.*$/gm, '');
            content = content.replace(/\/\*[\s\S]*?\*\//g, '');
            const settings = JSON.parse(content);
            const hooksRegistered = settings.hooks && settings.hooks.SessionStart ? 'yes' : 'no';
            console.log(`${COLORS.bright}Hooks Registered:${COLORS.reset} ${hooksRegistered}`);
        } catch {
            console.log(`${COLORS.bright}Hooks Registered:${COLORS.reset} unknown`);
        }
    }
}

function showStats(targetDir) {
    const memoryDir = path.join(targetDir, 'memory');
    
    if (!fs.existsSync(memoryDir)) {
        log.warn('No memory directory found. Run some sessions first to generate statistics.');
        return;
    }
    
    log.header('📊 DROIDPARTMENT STATISTICS');
    console.log('');
    
    // ═══════════════════════════════════════════════════════════════
    // DROID USAGE
    // ═══════════════════════════════════════════════════════════════
    console.log(`${COLORS.bright}🤖 DROID USAGE:${COLORS.reset}`);
    const droidUsageFile = path.join(memoryDir, 'droid_usage.json');
    if (fs.existsSync(droidUsageFile)) {
        try {
            const droidStats = JSON.parse(fs.readFileSync(droidUsageFile, 'utf8'));
            const totalCalls = droidStats.total_calls || 0;
            const droids = droidStats.droids || {};
            
            console.log(`  Total agent calls: ${COLORS.cyan}${totalCalls}${COLORS.reset}`);
            console.log('');
            
            // Sort droids by usage
            const sortedDroids = Object.entries(droids).sort((a, b) => b[1] - a[1]);
            
            if (sortedDroids.length > 0) {
                console.log('  Agent breakdown:');
                for (const [name, count] of sortedDroids) {
                    const bar = '█'.repeat(Math.min(20, Math.round(count / totalCalls * 40)));
                    const pct = ((count / totalCalls) * 100).toFixed(1);
                    console.log(`    ${COLORS.cyan}${name.padEnd(15)}${COLORS.reset} ${bar} ${count} (${pct}%)`);
                }
            }
            console.log('');
            
            // Custom vs built-in droids
            const builtInDroids = ['dpt-memory', 'dpt-dev', 'dpt-qa', 'dpt-sec', 'dpt-review', 'dpt-output', 
                                   'dpt-lead', 'dpt-arch', 'dpt-product', 'dpt-scrum', 'dpt-research',
                                   'dpt-api', 'dpt-data', 'dpt-docs', 'dpt-ux', 'dpt-ops', 'dpt-perf', 'dpt-grammar'];
            let builtInCount = 0;
            let customCount = 0;
            for (const [name, count] of sortedDroids) {
                if (builtInDroids.includes(name)) {
                    builtInCount += count;
                } else {
                    customCount += count;
                }
            }
            console.log(`  Built-in agents: ${builtInCount} calls`);
            console.log(`  Custom agents:   ${customCount} calls`);
        } catch {
            console.log('  (no data yet)');
        }
    } else {
        console.log('  (no data yet)');
    }
    console.log('');
    
    // ═══════════════════════════════════════════════════════════════
    // TOOL USAGE
    // ═══════════════════════════════════════════════════════════════
    console.log(`${COLORS.bright}🔧 TOOL USAGE:${COLORS.reset}`);
    const toolStatsFile = path.join(memoryDir, 'tool_stats.json');
    if (fs.existsSync(toolStatsFile)) {
        try {
            const toolStats = JSON.parse(fs.readFileSync(toolStatsFile, 'utf8'));
            const totalExec = toolStats.total_executions || 0;
            const errors = toolStats.errors || 0;
            const tools = toolStats.tools || {};
            
            console.log(`  Total tool calls: ${COLORS.cyan}${totalExec}${COLORS.reset}`);
            console.log(`  Errors: ${errors > 0 ? COLORS.red : COLORS.green}${errors}${COLORS.reset}`);
            console.log('');
            
            // Sort tools by usage
            const sortedTools = Object.entries(tools)
                .map(([name, data]) => [name, typeof data === 'number' ? data : data.count || 0])
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10);
            
            if (sortedTools.length > 0) {
                console.log('  Top tools:');
                for (const [name, count] of sortedTools) {
                    console.log(`    ${name.padEnd(15)} ${count} calls`);
                }
            }
        } catch {
            console.log('  (no data yet)');
        }
    } else {
        console.log('  (no data yet)');
    }
    console.log('');
    
    // ═══════════════════════════════════════════════════════════════
    // SESSION HISTORY
    // ═══════════════════════════════════════════════════════════════
    console.log(`${COLORS.bright}📅 SESSION HISTORY:${COLORS.reset}`);
    const sessionHistoryFile = path.join(memoryDir, 'session_history.json');
    if (fs.existsSync(sessionHistoryFile)) {
        try {
            const history = JSON.parse(fs.readFileSync(sessionHistoryFile, 'utf8'));
            const sessions = history.sessions || [];
            
            console.log(`  Total sessions: ${COLORS.cyan}${sessions.length}${COLORS.reset}`);
            
            if (sessions.length > 0) {
                // Recent sessions
                const recent = sessions.slice(-5).reverse();
                console.log('');
                console.log('  Recent sessions:');
                for (const s of recent) {
                    const date = s.started_at ? new Date(s.started_at).toLocaleDateString() : 'unknown';
                    const agents = s.agents_run || 0;
                    const tools = s.tools_used || 0;
                    console.log(`    ${date}: ${agents} agents, ${tools} tools`);
                }
            }
        } catch {
            console.log('  (no data yet)');
        }
    } else {
        console.log('  (no data yet)');
    }
    console.log('');
    
    // ═══════════════════════════════════════════════════════════════
    // LEARNING STATS
    // ═══════════════════════════════════════════════════════════════
    console.log(`${COLORS.bright}🧠 LEARNING PROGRESS:${COLORS.reset}`);
    
    // Global learning
    const lessonsCount = countYamlEntries(path.join(memoryDir, 'lessons.yaml'));
    const patternsCount = countYamlEntries(path.join(memoryDir, 'patterns.yaml'));
    const mistakesCount = countYamlEntries(path.join(memoryDir, 'mistakes.yaml'));
    
    console.log(`  Global knowledge:`);
    console.log(`    Lessons learned:  ${COLORS.green}${lessonsCount}${COLORS.reset}`);
    console.log(`    Patterns found:   ${COLORS.cyan}${patternsCount}${COLORS.reset}`);
    console.log(`    Mistakes tracked: ${COLORS.yellow}${mistakesCount}${COLORS.reset}`);
    console.log('');
    
    // Project-specific learning
    const projects = getProjectMemories(memoryDir);
    if (projects.length > 0) {
        console.log(`  Project knowledge (${projects.length} projects):`);
        
        let totalProjectLessons = 0;
        let totalProjectMistakes = 0;
        let totalProjectPatterns = 0;
        let totalProjectSessions = 0;
        
        for (const proj of projects) {
            totalProjectLessons += proj.lessons || 0;
            totalProjectMistakes += proj.mistakes || 0;
            totalProjectPatterns += proj.patterns || 0;
            totalProjectSessions += proj.sessions || 0;
        }
        
        console.log(`    Total lessons:  ${COLORS.green}${totalProjectLessons}${COLORS.reset} across projects`);
        console.log(`    Total mistakes: ${COLORS.yellow}${totalProjectMistakes}${COLORS.reset} tracked`);
        console.log(`    Total patterns: ${COLORS.cyan}${totalProjectPatterns}${COLORS.reset} identified`);
        console.log(`    Total sessions: ${COLORS.cyan}${totalProjectSessions}${COLORS.reset} recorded`);
        console.log('');
        
        // Per-project breakdown
        console.log('  Per-project breakdown:');
        for (const proj of projects.slice(0, 10)) {
            const stats = [];
            if (proj.lessons > 0) stats.push(`${proj.lessons}L`);
            if (proj.mistakes > 0) stats.push(`${proj.mistakes}M`);
            if (proj.patterns > 0) stats.push(`${proj.patterns}P`);
            if (proj.sessions > 0) stats.push(`${proj.sessions}S`);
            const statsStr = stats.length > 0 ? stats.join('/') : 'new';
            console.log(`    ${COLORS.cyan}${proj.name.substring(0, 30).padEnd(30)}${COLORS.reset} ${statsStr}`);
        }
        if (projects.length > 10) {
            console.log(`    ... and ${projects.length - 10} more projects`);
        }
    }
    console.log('');
    
    // ═══════════════════════════════════════════════════════════════
    // BRAIN EFFICIENCY
    // ═══════════════════════════════════════════════════════════════
    console.log(`${COLORS.bright}⚡ BRAIN EFFICIENCY:${COLORS.reset}`);
    
    // Calculate efficiency metrics
    const droidUsage = fs.existsSync(droidUsageFile) ? JSON.parse(fs.readFileSync(droidUsageFile, 'utf8')) : {};
    const totalAgentCalls = droidUsage.total_calls || 0;
    
    // Memory agent usage (shows learning discipline)
    const memoryAgentCalls = (droidUsage.droids || {})['dpt-memory'] || 0;
    const memoryRatio = totalAgentCalls > 0 ? ((memoryAgentCalls / totalAgentCalls) * 100).toFixed(1) : 0;
    
    // Learning rate - use global sessions if project sessions are 0
    const totalLearning = lessonsCount + patternsCount;
    let sessionCount = projects.reduce((sum, p) => sum + p.sessions, 0);
    
    // Fallback to global session history if project sessions are 0
    if (sessionCount === 0) {
        const sessionHistoryFile = path.join(memoryDir, 'session_history.json');
        if (fs.existsSync(sessionHistoryFile)) {
            try {
                const history = JSON.parse(fs.readFileSync(sessionHistoryFile, 'utf8'));
                sessionCount = (history.sessions || []).length;
            } catch {}
        }
    }
    
    // If still 0, estimate from droid calls (assume ~3 agent calls per session)
    if (sessionCount === 0 && totalAgentCalls > 0) {
        sessionCount = Math.ceil(totalAgentCalls / 3);
    }
    
    const learningRate = sessionCount > 0 ? (totalLearning / sessionCount).toFixed(2) : 'N/A';
    
    // Mistake prevention potential
    const preventionPotential = mistakesCount * 5; // Each mistake could prevent 5 future issues
    
    console.log(`  Memory agent usage: ${memoryRatio}% of calls (higher = better learning discipline)`);
    console.log(`  Learning rate: ${learningRate} lessons/session`);
    console.log(`  Mistake prevention: ~${preventionPotential} potential issues avoided`);
    console.log('');
    
    log.success('Statistics generated from ~/.factory/memory/');
}

// Parse arguments into command and flags
function parseArgs(args) {
    const result = {
        command: null,
        flags: {
            yes: false,
            quiet: false,
            verbose: false,
            project: false,
            force: false,
            dryRun: false,
            purge: false,
            version: false,
            help: false
        }
    };
    
    const commands = ['install', 'update', 'uninstall', 'reinstall', 'status', 'memory', 'stats'];
    
    for (const arg of args) {
        if (commands.includes(arg)) {
            result.command = arg;
        } else if (arg === '-y' || arg === '--yes') {
            result.flags.yes = true;
        } else if (arg === '-q' || arg === '--quiet') {
            result.flags.quiet = true;
        } else if (arg === '-v' || arg === '--verbose') {
            result.flags.verbose = true;
        } else if (arg === '--project') {
            result.flags.project = true;
        } else if (arg === '--force') {
            result.flags.force = true;
        } else if (arg === '--dry-run') {
            result.flags.dryRun = true;
        } else if (arg === '--purge' || arg === '--purge-memory') {
            result.flags.purge = true;
        } else if (arg === '--version') {
            result.flags.version = true;
        } else if (arg === '-h' || arg === '--help') {
            result.flags.help = true;
        } else if (arg === '-u') {
            result.command = 'uninstall'; // Legacy support
        } else if (arg === '-m') {
            result.command = 'memory'; // Legacy support
        } else if (arg === '--check') {
            result.command = 'status'; // Legacy support
        } else if (arg === '--stats') {
            result.command = 'stats'; // Show statistics
        } else if (arg === '--update') {
            result.flags.force = true; // Legacy: --update means force update
        } else if (arg.startsWith('-')) {
            log.warn(`Unknown option: ${arg}`);
        }
    }
    
    return result;
}

async function main() {
    const args = process.argv.slice(2);
    const { command, flags } = parseArgs(args);
    
    // Set global flags
    if (flags.quiet) VERBOSITY = 0;
    if (flags.verbose) VERBOSITY = 2;
    DRY_RUN = flags.dryRun;
    
    // Handle --version (always works, even in quiet mode)
    if (flags.version) {
        console.log(`droidpartment v${CURRENT_VERSION}`);
        process.exit(EXIT_SUCCESS);
        return;
    }
    
    // Handle --help
    if (flags.help) {
        showHelp();
        process.exit(EXIT_SUCCESS);
        return;
    }
    
    if (DRY_RUN) {
        log.warn('DRY-RUN MODE: No changes will be made');
    }
    
    showBanner();
    
    // Route to appropriate command
    const autoYes = flags.yes;
    const forceProject = flags.project;
    const forceUpdate = flags.force;
    const purgeMemory = flags.purge;
    
    // Handle status command
    if (command === 'status') {
        checkInstallation();
        process.exit(EXIT_SUCCESS);
        return;
    }
    
    // Handle stats command
    if (command === 'stats') {
        showStats(PERSONAL_DIR);
        process.exit(EXIT_SUCCESS);
        return;
    }
    
    // Handle memory command
    if (command === 'memory') {
        const personalInstalled = isInstalled(PERSONAL_DIR);
        const projectInstalled = isInstalled(PROJECT_DIR);
        
        if (!personalInstalled && !projectInstalled) {
            log.header('NOT INSTALLED');
            log.warn('Droidpartment is not installed yet.');
            log.info('Run: npx droidpartment install');
            process.exit(EXIT_NOT_INSTALLED);
            return;
        }
        
        const targetDir = forceProject ? PROJECT_DIR : (personalInstalled ? PERSONAL_DIR : PROJECT_DIR);
        await manageMemory(targetDir);
        process.exit(EXIT_SUCCESS);
        return;
    }
    
    // Handle reinstall command (uninstall + install)
    if (command === 'reinstall') {
        const personalInstalled = isInstalled(PERSONAL_DIR);
        const projectInstalled = isInstalled(PROJECT_DIR);
        const targetDir = forceProject ? PROJECT_DIR : PERSONAL_DIR;
        
        if (personalInstalled || projectInstalled) {
            const installedDir = personalInstalled ? PERSONAL_DIR : PROJECT_DIR;
            log.info('Uninstalling current installation...');
            if (!DRY_RUN) {
                await uninstall(installedDir, true, purgeMemory);
            } else {
                log.dryRun(`Would uninstall from ${installedDir}`);
            }
        }
        
        log.info('Installing fresh...');
        if (!DRY_RUN) {
            install(targetDir);
        } else {
            log.dryRun(`Would install to ${targetDir}`);
        }
        process.exit(EXIT_SUCCESS);
        return;
    }
    
    // Handle uninstall command
    if (command === 'uninstall') {
        const personalInstalled = isInstalled(PERSONAL_DIR);
        const projectInstalled = isInstalled(PROJECT_DIR);
        
        if (!personalInstalled && !projectInstalled) {
            log.header('NOTHING TO UNINSTALL');
            log.info('Droidpartment is not installed anywhere.');
            log.success('Already clean!');
            process.exit(EXIT_SUCCESS);
            return;
        }
        
        let targetDir;
        if (autoYes) {
            targetDir = forceProject ? PROJECT_DIR : (personalInstalled ? PERSONAL_DIR : PROJECT_DIR);
        } else if (personalInstalled && projectInstalled) {
            console.log('Droidpartment found in both locations:');
            console.log('');
            console.log(`  ${COLORS.green}1${COLORS.reset}) Personal (${PERSONAL_DIR})`);
            console.log(`  ${COLORS.yellow}2${COLORS.reset}) Project (${PROJECT_DIR})`);
            console.log(`  ${COLORS.red}3${COLORS.reset}) Both`);
            console.log('');
            const choice = await prompt('Which to uninstall? [1/2/3]', '1');
            if (choice === '3') {
                if (!DRY_RUN) {
                    await uninstall(PERSONAL_DIR, autoYes, purgeMemory);
                    await uninstall(PROJECT_DIR, autoYes, purgeMemory);
                } else {
                    log.dryRun('Would uninstall from both locations');
                }
                process.exit(EXIT_SUCCESS);
                return;
            }
            targetDir = choice === '2' ? PROJECT_DIR : PERSONAL_DIR;
        } else {
            targetDir = personalInstalled ? PERSONAL_DIR : PROJECT_DIR;
            log.info(`Found installation in: ${targetDir}`);
        }
        
        if (!DRY_RUN) {
            await uninstall(targetDir, autoYes, purgeMemory);
        } else {
            log.dryRun(`Would uninstall from ${targetDir}`);
        }
        process.exit(EXIT_SUCCESS);
        return;
    }
    
    // Check for existing installation
    const personalInstalled = getInstalledVersion(PERSONAL_DIR);
    const projectInstalled = getInstalledVersion(PROJECT_DIR);
    
    // Determine target and action
    let targetDir;
    let action = 'install'; // install, update, or skip
    
    if (personalInstalled || projectInstalled) {
        // Existing installation found
        const installedDir = personalInstalled ? PERSONAL_DIR : PROJECT_DIR;
        const installedVersion = personalInstalled || projectInstalled;
        
        log.header('EXISTING INSTALLATION DETECTED');
        console.log(`${COLORS.bright}Installed:${COLORS.reset} v${installedVersion} in ${installedDir}`);
        console.log(`${COLORS.bright}Available:${COLORS.reset} v${CURRENT_VERSION}`);
        console.log('');
        
        const versionCompare = compareVersions(CURRENT_VERSION, installedVersion);
        
        if (versionCompare > 0) {
            // Newer version available
            log.info(`${COLORS.green}Update available!${COLORS.reset}`);
            console.log('');
            
            if (autoYes || forceUpdate) {
                targetDir = installedDir;
                action = 'update';
            } else {
                console.log('What would you like to do?');
                console.log('');
                console.log(`  ${COLORS.green}1${COLORS.reset}) Update to v${CURRENT_VERSION} ${COLORS.cyan}← recommended${COLORS.reset}`);
                console.log(`  ${COLORS.yellow}2${COLORS.reset}) Reinstall (fresh install)`);
                console.log(`  ${COLORS.red}3${COLORS.reset}) Cancel`);
                console.log('');
                const choice = await prompt('Select option [1/2/3]', '1');
                
                if (choice === '1') {
                    targetDir = installedDir;
                    action = 'update';
                } else if (choice === '2') {
                    await uninstall(installedDir, autoYes, purgeMemory);
                    targetDir = installedDir;
                    action = 'install';
                } else {
                    log.info('Cancelled.');
                    return;
                }
            }
        } else if (versionCompare === 0) {
            // Same version
            log.success('Already up to date!');
            console.log('');
            
            if (forceUpdate) {
                // Force refresh even with same version
                log.info('Force update requested - refreshing files...');
                targetDir = installedDir;
                action = 'update';
            } else if (!autoYes) {
                console.log('What would you like to do?');
                console.log('');
                console.log(`  ${COLORS.green}1${COLORS.reset}) Exit (already installed)`);
                console.log(`  ${COLORS.yellow}2${COLORS.reset}) Reinstall (refresh files)`);
                console.log(`  ${COLORS.red}3${COLORS.reset}) Uninstall`);
                console.log('');
                const choice = await prompt('Select option [1/2/3]', '1');
                
                if (choice === '2') {
                    targetDir = installedDir;
                    action = 'update';
                } else if (choice === '3') {
                    await uninstall(installedDir, autoYes, purgeMemory);
                    return;
                } else {
                    log.info('No changes made.');
                    return;
                }
            } else {
                log.info('No changes needed.');
                return;
            }
        } else {
            // Older version in package (shouldn't happen normally)
            log.warn('Installed version is newer than package version.');
            log.info('Run with --update to force refresh.');
            return;
        }
    } else {
        // Fresh install
        log.header('DROIDPARTMENT INSTALLER');
        showAgentList();
        
        if (autoYes) {
            targetDir = forceProject ? PROJECT_DIR : PERSONAL_DIR;
            log.info(`Auto-installing to: ${targetDir}`);
        } else {
            console.log('Where would you like to install?');
            console.log('');
            console.log(`  ${COLORS.green}1${COLORS.reset}) Personal (${PERSONAL_DIR}) ${COLORS.cyan}← recommended${COLORS.reset}`);
            console.log('     Works in ALL projects automatically');
            console.log('');
            console.log(`  ${COLORS.yellow}2${COLORS.reset}) Project (${PROJECT_DIR})`);
            console.log('     Only this project, can commit to git');
            console.log('');
            
            const choice = await prompt('Select option [1/2]', '1');
            targetDir = choice === '2' ? PROJECT_DIR : PERSONAL_DIR;
        }
        action = 'install';
    }

    log.info(`Target: ${targetDir}`);
    
    // Execute action
    if (action === 'update') {
        const installedVersion = getInstalledVersion(targetDir);
        update(targetDir, installedVersion);
    } else {
        install(targetDir);
    }
}

main().catch(err => {
    log.error(`Failed: ${err.message}`);
    process.exit(1);
});
