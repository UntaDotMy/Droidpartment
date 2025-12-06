#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');
const PERSONAL_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.factory');
const PROJECT_DIR = path.join(process.cwd(), '.factory');

// Get version from package.json
const PACKAGE_JSON = require(path.join(__dirname, '..', 'package.json'));
const CURRENT_VERSION = PACKAGE_JSON.version;

const DROIDS = [
    'dpt-chief', 'dpt-memory', 'dpt-research', 'dpt-scrum', 'dpt-product', 'dpt-arch', 
    'dpt-dev', 'dpt-lead', 'dpt-qa', 'dpt-sec', 'dpt-ops',
    'dpt-docs', 'dpt-data', 'dpt-perf', 'dpt-ux', 'dpt-api', 'dpt-grammar', 'dpt-review',
    'dpt-output'
];

// Global memory files (shared across all projects)
const GLOBAL_MEMORY_FILES = ['lessons.yaml', 'patterns.yaml'];
// Per-project memory files (created when working on a project)
const PROJECT_MEMORY_FILES = ['episodic.yaml', 'semantic.yaml', 'index.yaml'];

const COLORS = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    red: '\x1b[31m'
};

const log = {
    info: (msg) => console.log(`${COLORS.blue}i${COLORS.reset} ${msg}`),
    success: (msg) => console.log(`${COLORS.green}✓${COLORS.reset} ${msg}`),
    warn: (msg) => console.log(`${COLORS.yellow}!${COLORS.reset} ${msg}`),
    error: (msg) => console.log(`${COLORS.red}✗${COLORS.reset} ${msg}`),
    header: (msg) => console.log(`\n${COLORS.bright}${COLORS.cyan}${msg}${COLORS.reset}\n`)
};

function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

function copyDir(src, dest) {
    ensureDir(dest);
    const entries = fs.readdirSync(src, { withFileTypes: true });
    let copied = 0;
    
    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        
        if (entry.isDirectory()) {
            copied += copyDir(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
            copied++;
        }
    }
    return copied;
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
    if (fs.existsSync(droidsDir) && fs.existsSync(path.join(droidsDir, 'dpt-chief.md'))) {
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
        const matches = content.match(/^- id:/gm);
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
            const episodes = countYamlEntries(path.join(projectPath, 'episodic.yaml'));
            const knowledge = countYamlEntries(path.join(projectPath, 'semantic.yaml'));
            const size = getFileSize(path.join(projectPath, 'episodic.yaml')) +
                        getFileSize(path.join(projectPath, 'semantic.yaml')) +
                        getFileSize(path.join(projectPath, 'index.yaml'));
            
            if (episodes > 0 || knowledge > 0 || size > 0) {
                projects.push({
                    name: entry.name,
                    episodes,
                    knowledge,
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
    const lessonsCount = countYamlEntries(lessonsFile);
    const patternsCount = countYamlEntries(patternsFile);
    const lessonsSize = getFileSize(lessonsFile);
    const patternsSize = getFileSize(patternsFile);
    const projects = getProjectMemories(memoryDir);
    
    // Display current status
    console.log(`${COLORS.bright}GLOBAL MEMORY:${COLORS.reset}`);
    console.log(`  Lessons:  ${lessonsCount} entries (${formatSize(lessonsSize)})`);
    console.log(`  Patterns: ${patternsCount} entries (${formatSize(patternsSize)})`);
    console.log('');
    
    console.log(`${COLORS.bright}PROJECT MEMORIES:${COLORS.reset}`);
    if (projects.length === 0) {
        console.log('  (none yet)');
    } else {
        for (const proj of projects) {
            console.log(`  ${COLORS.cyan}${proj.name}${COLORS.reset}: ${proj.episodes} episodes, ${proj.knowledge} knowledge (${formatSize(proj.size)})`);
        }
    }
    console.log('');
    
    // Menu
    console.log('What would you like to clean?');
    console.log('');
    console.log(`  ${COLORS.green}1${COLORS.reset}) Exit (keep all)`);
    console.log(`  ${COLORS.yellow}2${COLORS.reset}) Clear global lessons`);
    console.log(`  ${COLORS.yellow}3${COLORS.reset}) Clear global patterns`);
    console.log(`  ${COLORS.yellow}4${COLORS.reset}) Clear specific project memory`);
    console.log(`  ${COLORS.red}5${COLORS.reset}) Clear ALL global memory`);
    console.log(`  ${COLORS.red}6${COLORS.reset}) Clear ALL project memories`);
    console.log(`  ${COLORS.red}7${COLORS.reset}) Clear EVERYTHING (start fresh)`);
    console.log('');
    
    const choice = await prompt('Select option [1-7]', '1');
    
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
            if (projects.length === 0) {
                log.warn('No project memories to clear.');
            } else {
                console.log('');
                console.log('Which project memory to clear?');
                console.log('');
                projects.forEach((proj, i) => {
                    console.log(`  ${COLORS.yellow}${i + 1}${COLORS.reset}) ${proj.name} (${proj.episodes} episodes, ${proj.knowledge} knowledge)`);
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
            
        case '5':
            if (fs.existsSync(lessonsFile)) {
                fs.writeFileSync(lessonsFile, `# GLOBAL LESSONS - Universal Knowledge\nlessons: []\n`);
            }
            if (fs.existsSync(patternsFile)) {
                fs.writeFileSync(patternsFile, `# GLOBAL PATTERNS - Universal Truths\npatterns: []\n`);
            }
            log.success(`Cleared all global memory (${lessonsCount} lessons, ${patternsCount} patterns)`);
            break;
            
        case '6':
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
            
        case '7':
            // Clear global
            if (fs.existsSync(lessonsFile)) {
                fs.writeFileSync(lessonsFile, `# GLOBAL LESSONS - Universal Knowledge\nlessons: []\n`);
            }
            if (fs.existsSync(patternsFile)) {
                fs.writeFileSync(patternsFile, `# GLOBAL PATTERNS - Universal Truths\npatterns: []\n`);
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

function uninstall(targetDir) {
    // Check if installed
    if (!isInstalled(targetDir)) {
        log.header('NOTHING TO UNINSTALL');
        log.info(`Droidpartment is not installed in ${targetDir}`);
        log.success('Already clean!');
        return;
    }
    
    log.header('UNINSTALLING DROIDPARTMENT');
    
    let totalRemoved = 0;
    
    // Remove droids
    const droidsDir = path.join(targetDir, 'droids');
    if (fs.existsSync(droidsDir)) {
        for (const droid of DROIDS) {
            const droidFile = path.join(droidsDir, `${droid}.md`);
            if (fs.existsSync(droidFile)) {
                fs.unlinkSync(droidFile);
                log.success(`Removed ${droid}.md`);
                totalRemoved++;
            }
        }
    }
    
    // Remove skills
    const skillsDir = path.join(targetDir, 'skills');
    const skillsToRemove = ['bug-sweep', 'codebase-analysis', 'memory'];
    for (const skill of skillsToRemove) {
        const skillDir = path.join(skillsDir, skill);
        if (fs.existsSync(skillDir)) {
            removeDir(skillDir);
            fs.rmdirSync(skillDir);
            log.success(`Removed skill: ${skill}`);
            totalRemoved++;
        }
    }
    
    // Remove memory directory completely
    const memoryDir = path.join(targetDir, 'memory');
    if (fs.existsSync(memoryDir)) {
        const memoryRemoved = removeDir(memoryDir);
        totalRemoved += memoryRemoved;
        try {
            fs.rmdirSync(memoryDir);
        } catch (e) {
            // Directory might not be empty or already removed
        }
        log.success(`Removed memory system (${memoryRemoved} files)`);
    }
    
    // Remove AGENTS.md
    const agentsMd = path.join(targetDir, 'AGENTS.md');
    if (fs.existsSync(agentsMd)) {
        fs.unlinkSync(agentsMd);
        log.success('Removed AGENTS.md');
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
    
    // Update droids (overwrite all)
    log.header('UPDATING AGENTS');
    const droidsSource = path.join(TEMPLATES_DIR, 'droids');
    const droidsTarget = path.join(targetDir, 'droids');
    ensureDir(droidsTarget);
    const droidsCopied = copyDir(droidsSource, droidsTarget);
    log.success(`Updated ${droidsCopied} agent(s)`);
    
    // Update skills
    const skillsSource = path.join(TEMPLATES_DIR, 'skills');
    const skillsTarget = path.join(targetDir, 'skills');
    if (fs.existsSync(skillsSource)) {
        ensureDir(skillsTarget);
        const skillsCopied = copyDir(skillsSource, skillsTarget);
        log.success(`Updated ${skillsCopied} skill file(s)`);
    }
    
    // Update AGENTS.md (always update)
    const agentsMdSource = path.join(TEMPLATES_DIR, 'AGENTS.md');
    if (fs.existsSync(agentsMdSource)) {
        const agentsMdTarget = path.join(targetDir, 'AGENTS.md');
        fs.copyFileSync(agentsMdSource, agentsMdTarget);
        log.success('Updated AGENTS.md orchestrator');
    }
    
    // NOTE: We don't update memory files to preserve learned data!
    log.info('Memory files preserved (learning data kept)');
    
    // Save new version
    saveVersion(targetDir, CURRENT_VERSION);
    
    log.header('UPDATE COMPLETE');
    console.log(`${COLORS.bright}Updated to:${COLORS.reset} v${CURRENT_VERSION}`);
    console.log('');
    log.info('Restart droid CLI to apply changes.');
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
                      ${COLORS.cyan}19 Specialized AI Agents (DPT_*)${COLORS.reset}
                              ${COLORS.yellow}v${CURRENT_VERSION}${COLORS.reset}
`);
}

function install(targetDir) {
    // Create directories
    const droidsTarget = path.join(targetDir, 'droids');
    const skillsTarget = path.join(targetDir, 'skills');
    
    ensureDir(droidsTarget);
    ensureDir(skillsTarget);
    
    // Copy droids
    log.header('INSTALLING AGENTS');
    const droidsSource = path.join(TEMPLATES_DIR, 'droids');
    const droidsCopied = copyDir(droidsSource, droidsTarget);
    log.success(`Installed ${droidsCopied} agent(s)`);
    
    // Copy skills
    const skillsSource = path.join(TEMPLATES_DIR, 'skills');
    if (fs.existsSync(skillsSource)) {
        const skillsCopied = copyDir(skillsSource, skillsTarget);
        log.success(`Installed ${skillsCopied} skill file(s)`);
    }
    
    // Copy memory system
    log.header('INSTALLING MEMORY SYSTEM');
    const memoryTarget = path.join(targetDir, 'memory');
    const memorySource = path.join(TEMPLATES_DIR, 'memory');
    ensureDir(memoryTarget);
    ensureDir(path.join(memoryTarget, 'projects')); // For per-project memories
    if (fs.existsSync(memorySource)) {
        const memoryCopied = copyDir(memorySource, memoryTarget);
        log.success(`Installed global memory (${memoryCopied} files)`);
        log.info('Global: lessons.yaml, patterns.yaml (shared across all projects)');
        log.info('Per-project: memory/projects/{project}/ (auto-created when needed)');
    }
    
    // Copy AGENTS.md
    const agentsMdSource = path.join(TEMPLATES_DIR, 'AGENTS.md');
    if (fs.existsSync(agentsMdSource)) {
        const agentsMdTarget = path.join(targetDir, 'AGENTS.md');
        fs.copyFileSync(agentsMdSource, agentsMdTarget);
        log.success('Installed AGENTS.md orchestrator');
    }
    
    // Save version
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
    console.log(`${COLORS.bright}Agents included:${COLORS.reset}`);
    console.log('');
    console.log('  Leader:');
    console.log('  • chief          - TEAM LEADER (entry point)');
    console.log('');
    console.log('  Core Team:');
    console.log('  • memory         - Human-like learning system');
    console.log('  • research       - Deep research, current content');
    console.log('  • scrum-master   - Task decomposition, DAG planning');
    console.log('  • product-owner  - Requirements, user stories');
    console.log('  • architect      - System design, patterns');
    console.log('  • developer      - Implementation, coding');
    console.log('  • tech-lead      - Code review, SOLID');
    console.log('  • qa-engineer    - Testing strategies');
    console.log('  • security       - OWASP 2025, vulnerabilities');
    console.log('  • devops         - CI/CD, deployment');
    console.log('');
    console.log('  Specialists:');
    console.log('  • documentation  - Clear, concise docs');
    console.log('  • database       - Schema, queries, data');
    console.log('  • performance    - Optimization (measure first)');
    console.log('  • ux-ui          - Simple, accessible interfaces');
    console.log('  • api-design     - RESTful, consistent APIs');
    console.log('  • grammar        - Grammar, clarity checker');
    console.log('  • reviewer       - Anti-over-engineering guard');
    console.log('  • output-rules   - Output formatting standards');
    console.log('');
    console.log('  Memory System (Grows Smarter Over Time):');
    console.log('  • GLOBAL: Lessons & patterns shared across ALL projects');
    console.log('  • PER-PROJECT: Specific knowledge per project (never mixed)');
    console.log('  • Starts empty like a child, becomes expert over time');
    console.log('  • More sessions = less mistakes = smarter');
    console.log('');
}

async function main() {
    const args = process.argv.slice(2);
    const isUninstall = args.includes('--uninstall') || args.includes('-u');
    const isMemory = args.includes('--memory') || args.includes('-m');
    const autoYes = args.includes('--yes') || args.includes('-y');
    const forceProject = args.includes('--project');
    const forceUpdate = args.includes('--update');
    
    showBanner();
    
    // Handle memory management
    if (isMemory) {
        const personalInstalled = isInstalled(PERSONAL_DIR);
        const projectInstalled = isInstalled(PROJECT_DIR);
        
        if (!personalInstalled && !projectInstalled) {
            log.header('NOT INSTALLED');
            log.warn('Droidpartment is not installed yet.');
            log.info('Run: npx droidpartment');
            return;
        }
        
        // Use the installed location
        const targetDir = forceProject ? PROJECT_DIR : (personalInstalled ? PERSONAL_DIR : PROJECT_DIR);
        await manageMemory(targetDir);
        return;
    }
    
    // Handle uninstall
    if (isUninstall) {
        const personalInstalled = isInstalled(PERSONAL_DIR);
        const projectInstalled = isInstalled(PROJECT_DIR);
        
        if (!personalInstalled && !projectInstalled) {
            log.header('NOTHING TO UNINSTALL');
            log.info('Droidpartment is not installed anywhere.');
            log.success('Already clean!');
            return;
        }
        
        let targetDir;
        if (autoYes) {
            targetDir = forceProject ? PROJECT_DIR : PERSONAL_DIR;
        } else if (personalInstalled && projectInstalled) {
            // Both installed, ask which one
            console.log('Droidpartment found in both locations:');
            console.log('');
            console.log(`  ${COLORS.green}1${COLORS.reset}) Personal (${PERSONAL_DIR})`);
            console.log(`  ${COLORS.yellow}2${COLORS.reset}) Project (${PROJECT_DIR})`);
            console.log(`  ${COLORS.red}3${COLORS.reset}) Both`);
            console.log('');
            const choice = await prompt('Which to uninstall? [1/2/3]', '1');
            if (choice === '3') {
                uninstall(PERSONAL_DIR);
                uninstall(PROJECT_DIR);
                return;
            }
            targetDir = choice === '2' ? PROJECT_DIR : PERSONAL_DIR;
        } else {
            // Only one installed, use that one
            targetDir = personalInstalled ? PERSONAL_DIR : PROJECT_DIR;
            log.info(`Found installation in: ${targetDir}`);
        }
        uninstall(targetDir);
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
                    uninstall(installedDir);
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
            
            if (!autoYes) {
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
                    uninstall(installedDir);
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
