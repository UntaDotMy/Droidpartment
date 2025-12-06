#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');
const PERSONAL_DIR = path.join(process.env.HOME || process.env.USERPROFILE, '.factory');
const PROJECT_DIR = path.join(process.cwd(), '.factory');

const DROIDS = [
    'chief', 'memory', 'research', 'scrum-master', 'product-owner', 'architect', 
    'developer', 'tech-lead', 'qa-engineer', 'security', 'devops',
    'documentation', 'database', 'performance', 'ux-ui', 'api-design', 'grammar', 'reviewer'
];

const MEMORY_FILES = ['episodic.yaml', 'semantic.yaml', 'lessons.yaml', 'index.yaml'];

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

function uninstall(targetDir) {
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
    
    // Remove memory directory
    const memoryDir = path.join(targetDir, 'memory');
    if (fs.existsSync(memoryDir)) {
        for (const file of MEMORY_FILES) {
            const memFile = path.join(memoryDir, file);
            if (fs.existsSync(memFile)) {
                fs.unlinkSync(memFile);
                totalRemoved++;
            }
        }
        log.success('Removed memory system');
    }
    
    // Remove AGENTS.md
    const agentsMd = path.join(targetDir, 'AGENTS.md');
    if (fs.existsSync(agentsMd)) {
        fs.unlinkSync(agentsMd);
        log.success('Removed AGENTS.md');
        totalRemoved++;
    }
    
    log.header('UNINSTALL COMPLETE');
    console.log(`Removed ${totalRemoved} items from ${targetDir}`);
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
 |____/|_| \\_\\\\___/|___|____/|_| /_/   \\_\\_| \\_\\|_| |_|  |_|_____|_| \\_| |_|  
                                                                              
${COLORS.reset}
           ${COLORS.bright}Autonomous Software Development Department${COLORS.reset}
                      ${COLORS.cyan}18 Specialized AI Agents (DPT_*)${COLORS.reset}
`);
}

async function main() {
    const args = process.argv.slice(2);
    const isUninstall = args.includes('--uninstall') || args.includes('-u');
    const autoYes = args.includes('--yes') || args.includes('-y');
    const forceProject = args.includes('--project');
    
    showBanner();
    
    // Handle uninstall
    if (isUninstall) {
        let targetDir;
        if (autoYes) {
            targetDir = forceProject ? PROJECT_DIR : PERSONAL_DIR;
        } else {
            console.log('Where do you want to uninstall from?');
            console.log('');
            console.log(`  ${COLORS.green}1${COLORS.reset}) Personal (${PERSONAL_DIR})`);
            console.log(`  ${COLORS.yellow}2${COLORS.reset}) Project (${PROJECT_DIR})`);
            console.log('');
            const choice = await prompt('Select option [1/2]', '1');
            targetDir = choice === '2' ? PROJECT_DIR : PERSONAL_DIR;
        }
        uninstall(targetDir);
        return;
    }
    
    // Install flow
    log.header('DROIDPARTMENT INSTALLER');
    
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
    console.log('');
    console.log('  Memory System:');
    console.log('  • Learns from mistakes automatically');
    console.log('  • Gains knowledge when you confirm fixes');
    console.log('  • Gets smarter with every project');
    console.log('');

    let targetDir;
    
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

    log.info(`Installing to: ${targetDir}`);
    
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
    if (fs.existsSync(memorySource)) {
        const memoryCopied = copyDir(memorySource, memoryTarget);
        log.success(`Installed memory system (${memoryCopied} files)`);
    }
    
    // Copy AGENTS.md
    const agentsMdSource = path.join(TEMPLATES_DIR, 'AGENTS.md');
    if (fs.existsSync(agentsMdSource)) {
        const agentsMdTarget = path.join(targetDir, 'AGENTS.md');
        fs.copyFileSync(agentsMdSource, agentsMdTarget);
        log.success('Installed AGENTS.md orchestrator');
    }

    // Summary
    log.header('INSTALLATION COMPLETE');
    
    console.log(`${COLORS.bright}Installed to:${COLORS.reset} ${targetDir}`);
    console.log('');
    
    log.header('NEXT STEPS');
    console.log('1. Enable Custom Droids in Factory:');
    console.log('   /settings → Experimental → Custom Droids');
    console.log('');
    console.log('2. Restart droid CLI');
    console.log('');
    console.log('3. Just describe your task - agents work automatically!');
    console.log('');
    console.log(`${COLORS.bright}To uninstall:${COLORS.reset}`);
    console.log('   npx droidpartment --uninstall');
    console.log('');
    
    log.success('Droidpartment is ready!');
}

main().catch(err => {
    log.error(`Failed: ${err.message}`);
    process.exit(1);
});
