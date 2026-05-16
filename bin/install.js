#!/usr/bin/env node
// Droidpartment v4 installer. See README.md for behavior; CHANGELOG.md for history.
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

const PACKAGE_JSON = require(path.join(__dirname, '..', 'package.json'));
const CURRENT_VERSION = PACKAGE_JSON.version;
const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');
const PERSONAL_DIR = path.join(process.env.HOME || process.env.USERPROFILE || os.homedir(), '.factory');
const PROJECT_DIR = path.join(process.cwd(), '.factory');
const MANIFEST_FILE = '.droidpartment-manifest.json';
const VERSION_FILE = '.droidpartment-version';
const BACKUP_RETAIN = 3;

const EXIT_OK = 0;
const EXIT_ERROR = 1;

const COLORS = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    red: '\x1b[31m',
    gray: '\x1b[90m',
};

let VERBOSITY = 1;
let DRY_RUN = false;

const log = {
    info: msg => VERBOSITY >= 1 && console.log(`${COLORS.blue}i${COLORS.reset} ${msg}`),
    ok: msg => VERBOSITY >= 1 && console.log(`${COLORS.green}+${COLORS.reset} ${msg}`),
    warn: msg => VERBOSITY >= 1 && console.log(`${COLORS.yellow}!${COLORS.reset} ${msg}`),
    err: msg => console.error(`${COLORS.red}x${COLORS.reset} ${msg}`),
    head: msg => VERBOSITY >= 1 && console.log(`\n${COLORS.bright}${COLORS.cyan}${msg}${COLORS.reset}\n`),
    verbose: msg => VERBOSITY >= 2 && console.log(`${COLORS.gray}  ${msg}${COLORS.reset}`),
    dry: msg => DRY_RUN && console.log(`${COLORS.yellow}[dry-run]${COLORS.reset} ${msg}`),
};

function ensureDir(dir) {
    if (DRY_RUN) {
        log.dry(`mkdir ${dir}`);
        return;
    }
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

function loadManifest(targetDir) {
    const p = path.join(targetDir, MANIFEST_FILE);
    if (!fs.existsSync(p)) return null;
    try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; }
}

function saveManifest(targetDir, manifest) {
    if (DRY_RUN) {
        log.dry(`write manifest -> ${path.join(targetDir, MANIFEST_FILE)}`);
        return;
    }
    fs.writeFileSync(path.join(targetDir, MANIFEST_FILE), JSON.stringify(manifest, null, 2));
}

function newManifest(version) {
    return {
        version,
        installedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        files: {},
        directories: [],
        binaryPath: null,
        settingsModified: false,
        hooksRegistered: [],
    };
}

function getInstalledVersion(targetDir) {
    const vp = path.join(targetDir, VERSION_FILE);
    if (fs.existsSync(vp)) return fs.readFileSync(vp, 'utf8').trim();
    if (fs.existsSync(path.join(targetDir, 'droids', 'dpt-memory.md'))) return 'legacy';
    return null;
}

function saveVersion(targetDir, version) {
    if (DRY_RUN) { log.dry(`write version ${version}`); return; }
    fs.writeFileSync(path.join(targetDir, VERSION_FILE), version);
}

function compareVersions(a, b) {
    if (a === 'legacy') return -1;
    if (b === 'legacy') return 1;
    const pa = a.split('.').map(Number), pb = b.split('.').map(Number);
    for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
        const x = pa[i] || 0, y = pb[i] || 0;
        if (x > y) return 1;
        if (x < y) return -1;
    }
    return 0;
}

function detectV3PythonInstall(targetDir) {
    const memoryDir = path.join(targetDir, 'memory');
    if (!fs.existsSync(memoryDir)) return false;
    if (fs.existsSync(path.join(memoryDir, 'hooks'))) return true;
    const entries = fs.readdirSync(memoryDir).filter(f => f.endsWith('.py'));
    return entries.length > 0;
}

function findPlatformBinary() {
    const platform = process.platform; // win32 | darwin | linux
    const arch = process.arch;          // x64 | arm64
    const ext = platform === 'win32' ? '.exe' : '';
    const pkgName = `@droidpartment/cli-${platform}-${arch}`;

    // 1. Try resolved optional dependency
    try {
        const pkgPath = require.resolve(`${pkgName}/package.json`, { paths: [path.join(__dirname, '..')] });
        const pkgDir = path.dirname(pkgPath);
        const candidate = path.join(pkgDir, 'bin', `dpt${ext}`);
        if (fs.existsSync(candidate)) return candidate;
    } catch { /* not installed */ }

    // 2. Try local source build (developer / monorepo install)
    const localBuild = path.join(__dirname, '..', 'rust', 'target', 'release', `dpt${ext}`);
    if (fs.existsSync(localBuild)) return localBuild;

    return null;
}

function copyBinary(targetDir, manifest) {
    const platform = process.platform;
    const ext = platform === 'win32' ? '.exe' : '';
    const binSrc = findPlatformBinary();
    if (!binSrc) {
        log.err(`No native dpt binary available for ${platform}-${process.arch}.`);
        log.info('Make sure your npm install completed (the platform package is an optional dependency).');
        log.info('Or build from source: cd rust && cargo build --release');
        return null;
    }

    const binDir = path.join(targetDir, 'bin');
    ensureDir(binDir);
    const binDest = path.join(binDir, `dpt${ext}`);

    if (DRY_RUN) {
        log.dry(`copy ${binSrc} -> ${binDest}`);
        return binDest;
    }

    // On Windows, replacing a running exe needs MoveFileEx-style semantics. Best-effort fallback.
    try {
        if (fs.existsSync(binDest)) {
            try { fs.unlinkSync(binDest); }
            catch (e) {
                const stash = `${binDest}.old-${Date.now()}`;
                fs.renameSync(binDest, stash);
                log.verbose(`stashed running binary as ${path.basename(stash)}`);
            }
        }
        fs.copyFileSync(binSrc, binDest);
        if (platform !== 'win32') {
            fs.chmodSync(binDest, 0o755);
        }
        log.verbose(`installed binary ${binDest}`);
    } catch (e) {
        log.err(`failed to install binary: ${e.message}`);
        return null;
    }

    const rel = path.relative(targetDir, binDest);
    manifest.files[rel] = {
        size: fs.statSync(binDest).size,
        type: 'binary',
    };
    manifest.binaryPath = rel;
    if (!manifest.directories.includes('bin')) manifest.directories.push('bin');

    return binDest;
}

function copyTreeTracked(srcRoot, destRoot, manifest, baseDir, opts = {}) {
    const skipNames = new Set(opts.skipNames || []);
    const preserveExisting = new Set(opts.preserveExisting || []);
    let count = 0;

    function walk(src, dest) {
        if (skipNames.has(path.basename(src))) return;
        ensureDir(dest);
        const relDir = path.relative(baseDir, dest);
        if (relDir && !manifest.directories.includes(relDir)) {
            manifest.directories.push(relDir);
        }
        for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
            if (skipNames.has(entry.name)) continue;
            const sp = path.join(src, entry.name);
            const dp = path.join(dest, entry.name);
            if (entry.isDirectory()) {
                walk(sp, dp);
            } else {
                if (DRY_RUN) {
                    log.dry(`copy ${sp} -> ${dp}`);
                    continue;
                }
                if (preserveExisting.has(entry.name) && fs.existsSync(dp)) {
                    log.verbose(`preserved ${path.relative(baseDir, dp)}`);
                } else {
                    fs.copyFileSync(sp, dp);
                    count++;
                }
                const rel = path.relative(baseDir, dp);
                manifest.files[rel] = {
                    size: fs.statSync(dp).size,
                    type: path.extname(entry.name).slice(1) || 'file',
                };
            }
        }
    }
    if (fs.existsSync(srcRoot)) walk(srcRoot, destRoot);
    return count;
}

function copyFileTracked(src, dest, manifest, baseDir) {
    if (!fs.existsSync(src)) return false;
    if (DRY_RUN) {
        log.dry(`copy ${src} -> ${dest}`);
        return true;
    }
    ensureDir(path.dirname(dest));
    fs.copyFileSync(src, dest);
    const rel = path.relative(baseDir, dest);
    manifest.files[rel] = {
        size: fs.statSync(dest).size,
        type: path.extname(dest).slice(1) || 'file',
    };
    return true;
}

function removeDir(dir) {
    if (!fs.existsSync(dir)) return 0;
    let n = 0;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const p = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            n += removeDir(p);
            try { fs.rmdirSync(p); } catch {}
        } else {
            try { fs.unlinkSync(p); n++; } catch {}
        }
    }
    return n;
}

function migrateFromV3Python(targetDir) {
    const memoryDir = path.join(targetDir, 'memory');
    if (!fs.existsSync(memoryDir)) return 0;

    log.head('MIGRATING FROM v3 (Python -> Rust)');
    let removed = 0;

    // 1. Remove ~/.factory/memory/hooks/ entirely
    const hooksDir = path.join(memoryDir, 'hooks');
    if (fs.existsSync(hooksDir)) {
        if (DRY_RUN) {
            log.dry(`rm -rf ${hooksDir}`);
        } else {
            removed += removeDir(hooksDir);
            try { fs.rmdirSync(hooksDir); } catch {}
            log.ok(`removed memory/hooks/ (${removed} files)`);
        }
    }

    // 2. Remove top-level Python modules in memory/
    for (const f of fs.readdirSync(memoryDir)) {
        if (f.endsWith('.py') || f.endsWith('.pyc') || f === '__pycache__') {
            const fp = path.join(memoryDir, f);
            if (DRY_RUN) { log.dry(`rm ${fp}`); continue; }
            try {
                if (fs.statSync(fp).isDirectory()) {
                    removeDir(fp);
                    fs.rmdirSync(fp);
                } else {
                    fs.unlinkSync(fp);
                }
                removed++;
            } catch {}
        }
    }

    // 3. Remove old droid_usage.json / tool_stats.json / session_history.json (schema may differ)
    for (const f of ['session_history.json']) {
        const fp = path.join(memoryDir, f);
        if (fs.existsSync(fp)) {
            if (DRY_RUN) { log.dry(`rm ${fp}`); continue; }
            try { fs.unlinkSync(fp); removed++; } catch {}
        }
    }

    // 4. Move Stat files to new location memory/stats/ (Rust stats.rs writes there)
    const statsDir = path.join(memoryDir, 'stats');
    ensureDir(statsDir);

    log.ok(`migration complete (${removed} legacy files removed)`);
    log.info('Preserved: lessons.yaml, patterns.yaml, mistakes.yaml, stats.yaml, projects/');
    return removed;
}

function isInstalled(targetDir) {
    return fs.existsSync(path.join(targetDir, VERSION_FILE)) ||
           fs.existsSync(path.join(targetDir, 'droids', 'dpt-memory.md'));
}

function dptBinaryAt(targetDir) {
    const ext = process.platform === 'win32' ? '.exe' : '';
    return path.join(targetDir, 'bin', `dpt${ext}`);
}

function settingsPathFor(targetDir) {
    // Project install -> project-local settings; personal install -> ~/.factory/settings.json.
    if (targetDir === PROJECT_DIR) return path.join(targetDir, 'settings.json');
    return path.join(process.env.HOME || process.env.USERPROFILE || os.homedir(), '.factory', 'settings.json');
}

function backupSettings(settingsPath) {
    if (!fs.existsSync(settingsPath)) return null;
    const stamp = new Date().toISOString().replace(/[:.]/g, '-');
    const dest = `${settingsPath}.bak-${stamp}`;
    fs.copyFileSync(settingsPath, dest);
    if (process.platform !== 'win32') {
        try { fs.chmodSync(dest, 0o600); } catch {}
    }
    pruneBackups(settingsPath);
    return dest;
}

function pruneBackups(settingsPath) {
    const dir = path.dirname(settingsPath);
    const baseName = path.basename(settingsPath);
    let entries;
    try { entries = fs.readdirSync(dir); } catch { return; }
    const baks = entries
        .filter(f => f.startsWith(baseName + '.bak-'))
        .map(f => ({ name: f, full: path.join(dir, f), mtime: 0 }));
    for (const b of baks) {
        try { b.mtime = fs.statSync(b.full).mtimeMs; } catch {}
    }
    baks.sort((a, b) => b.mtime - a.mtime);
    for (const old of baks.slice(BACKUP_RETAIN)) {
        try { fs.unlinkSync(old.full); } catch {}
    }
}

function readSettingsStrict(settingsPath) {
    // Returns { settings, raw, parseError }. Never silently defaults to {}.
    if (!fs.existsSync(settingsPath)) return { settings: {}, raw: null, parseError: null };
    let raw = fs.readFileSync(settingsPath, 'utf8');
    if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
    try {
        return { settings: JSON.parse(raw), raw, parseError: null };
    } catch (e) {
        return { settings: null, raw, parseError: e };
    }
}

function readEffectiveSettings(settingsPath) {
    // Read settings.json + settings.local.json overlay (per Droid docs).
    const base = readSettingsStrict(settingsPath);
    if (base.parseError || !base.settings) return base;
    const localPath = settingsPath.replace(/settings\.json$/, 'settings.local.json');
    if (!fs.existsSync(localPath)) return base;
    const local = readSettingsStrict(localPath);
    if (local.parseError || !local.settings) {
        log.warn(`settings.local.json could not be parsed; ignoring overlay: ${local.parseError && local.parseError.message}`);
        return base;
    }
    return { settings: { ...base.settings, ...local.settings }, raw: base.raw, parseError: null };
}

function isOurHookEntry(entry) {
    // "Our" entries point at dpt(.exe) hook <event> or the legacy python hook-*.py.
    if (!entry || !Array.isArray(entry.hooks)) return false;
    return entry.hooks.every(h => {
        const cmd = String(h && h.command || '');
        // Allow any non-word characters (quotes, slashes, spaces) between dpt[.exe] and `hook`.
        return /\bdpt(\.exe)?\b[^\w]+hook\b/i.test(cmd) || /hook-[a-z-]+\.py\b/i.test(cmd);
    });
}

function registerHooks(targetDir, dptBinary, manifest) {
    const settingsPath = settingsPathFor(targetDir);
    ensureDir(path.dirname(settingsPath));

    const { settings, raw, parseError } = readSettingsStrict(settingsPath);
    if (parseError) {
        log.err(`Refusing to modify ${settingsPath}: existing JSON is not parseable.`);
        log.err(`  Reason: ${parseError.message}`);
        log.info(`  Fix the file by hand, or use \`dpt install-hooks\` and merge the printed block yourself.`);
        log.info(`  The original file has not been touched.`);
        return false;
    }

    // Honor settings.local.json overlay for the hooksDisabled flag (per Droid settings docs).
    const effective = readEffectiveSettings(settingsPath).settings || settings || {};
    if (effective.hooksDisabled === true) {
        log.warn(`hooksDisabled is true (effective via settings.json or settings.local.json); skipping hook registration.`);
        log.info('  Set hooksDisabled to false (or remove it) and re-run install to enable Droidpartment hooks.');
        manifest.settingsModified = false;
        manifest.hooksRegistered = [];
        return true;
    }

    const next = settings || {};
    if (!next.hooks || typeof next.hooks !== 'object') next.hooks = {};

    const bin = dptBinary.replace(/\\/g, '/');
    // Only quote the path when it actually contains spaces. Some shells (notably
    // cmd.exe via Droid's hook runner) re-escape outer quotes which can turn
    // `"path"` into the literal `\"path\"` and break execution.
    const quoted = bin.includes(' ') ? `"${bin}"` : bin;
    const cmd = arg => `${quoted} hook ${arg}`;

    const events = [
        ['SessionStart', '*', 'session-start', 15],
        ['UserPromptSubmit', '*', 'user-prompt-submit', 5],
        ['PreToolUse', '*', 'pre-tool-use', 5],
        ['PostToolUse', '*', 'post-tool-use', 5],
        ['Stop', '*', 'stop', 5],
        ['SubagentStop', '*', 'subagent-stop', 5],
        ['SessionEnd', '*', 'session-end', 10],
        ['PreCompact', '*', 'pre-compact', 5],
        ['Notification', '', 'notification', 5],
    ];

    const ourEntry = (matcher, sub, timeout) => ({
        matcher,
        hooks: [{ type: 'command', command: cmd(sub), timeout }],
    });

    let added = 0, replaced = 0, kept = 0;
    for (const [event, matcher, sub, timeout] of events) {
        const handlers = Array.isArray(next.hooks[event]) ? next.hooks[event].slice() : [];
        // Drop any existing Droidpartment-owned entries; keep everything else verbatim.
        const others = handlers.filter(h => !isOurHookEntry(h));
        const ourCount = handlers.length - others.length;
        kept += others.length;
        others.push(ourEntry(matcher, sub, timeout));
        if (ourCount > 0) replaced++;
        else added++;
        next.hooks[event] = others;
    }

    if (DRY_RUN) {
        log.dry(`would write ${settingsPath} (added ${added}, replaced ${replaced}, kept ${kept} unrelated)`);
        return true;
    }

    if (raw !== null) {
        const bakPath = backupSettings(settingsPath);
        if (bakPath) log.verbose(`backup: ${bakPath}`);
    }

    fs.writeFileSync(settingsPath, JSON.stringify(next, null, 2));
    log.ok(`updated ${settingsPath} (added ${added}, replaced ${replaced}, kept ${kept} unrelated entries)`);

    manifest.settingsModified = true;
    manifest.settingsPath = settingsPath;
    manifest.hooksRegistered = events.map(e => e[0]);
    return true;
}

function unregisterHooks(targetDir) {
    const settingsPath = settingsPathFor(targetDir);
    if (!fs.existsSync(settingsPath)) return;
    const { settings, parseError } = readSettingsStrict(settingsPath);
    if (parseError) {
        log.warn(`could not parse ${settingsPath}: ${parseError.message}`);
        log.info('skipping hook removal; please remove dpt hook entries manually');
        return;
    }
    if (!settings.hooks) return;

    const bakPath = backupSettings(settingsPath);
    if (bakPath) log.verbose(`backup: ${bakPath}`);

    let changed = false;
    for (const event of ['SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PostToolUse', 'Stop', 'SubagentStop', 'SessionEnd', 'PreCompact', 'Notification']) {
        const handlers = settings.hooks[event];
        if (!Array.isArray(handlers)) continue;
        const filtered = handlers.filter(h => !isOurHookEntry(h));
        if (filtered.length === handlers.length) continue;
        changed = true;
        if (filtered.length === 0) delete settings.hooks[event];
        else settings.hooks[event] = filtered;
    }
    if (changed) {
        if (Object.keys(settings.hooks).length === 0) delete settings.hooks;
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
        log.ok(`removed Droidpartment hooks from ${settingsPath}`);
    }
}

function install(targetDir) {
    log.head('INSTALLING DROIDPARTMENT v' + CURRENT_VERSION);
    ensureDir(targetDir);
    const previousManifest = loadManifest(targetDir);
    const manifest = newManifest(CURRENT_VERSION);

    if (detectV3PythonInstall(targetDir)) {
        migrateFromV3Python(targetDir);
    }

    log.head('INSTALLING NATIVE BINARY');
    const dptBin = copyBinary(targetDir, manifest);
    if (!dptBin) {
        log.err('cannot continue without dpt binary');
        return false;
    }
    log.ok(`dpt available at ${dptBin}`);

    log.head('INSTALLING SUB-DROIDS');
    const droidsDest = path.join(targetDir, 'droids');
    const c1 = copyTreeTracked(path.join(TEMPLATES_DIR, 'droids'), droidsDest, manifest, targetDir);
    log.ok(`installed ${c1} sub-droid file(s)`);

    log.head('INSTALLING SKILLS');
    const skillsDest = path.join(targetDir, 'skills');
    const c2 = copyTreeTracked(path.join(TEMPLATES_DIR, 'skills'), skillsDest, manifest, targetDir);
    log.ok(`installed ${c2} skill file(s)`);

    log.head('INSTALLING MEMORY DEFAULTS');
    const memoryDest = path.join(targetDir, 'memory');
    ensureDir(memoryDest);
    ensureDir(path.join(memoryDest, 'projects'));
    if (!manifest.directories.includes('memory')) manifest.directories.push('memory');
    if (!manifest.directories.includes('memory/projects')) manifest.directories.push('memory/projects');
    const memorySrc = path.join(TEMPLATES_DIR, 'memory');
    if (fs.existsSync(memorySrc)) {
        const preserve = ['lessons.yaml', 'patterns.yaml', 'mistakes.yaml', 'stats.yaml'];
        const c3 = copyTreeTracked(memorySrc, memoryDest, manifest, targetDir, { preserveExisting: preserve });
        log.ok(`installed ${c3} memory template file(s)`);
    }

    const agentsSrc = path.join(TEMPLATES_DIR, 'AGENTS.md');
    if (fs.existsSync(agentsSrc)) {
        copyFileTracked(agentsSrc, path.join(targetDir, 'AGENTS.md'), manifest, targetDir);
        log.ok('installed AGENTS.md');
    }

    // Note: templates/plugin/ is the source for the future plugin-marketplace
    // distribution. The npm-install path does not copy it because that would
    // duplicate hook registrations.

    log.head('REGISTERING HOOKS');
    const ok = registerHooks(targetDir, dptBin, manifest);
    if (!ok) {
        log.warn('hooks were not registered - install otherwise complete');
    }

    // Delta-patch cleanup: remove files that were tracked in the previous
    // manifest but are not in the new one (e.g. retired slash commands).
    if (previousManifest && previousManifest.files) {
        const preserveBases = new Set(['lessons.yaml', 'patterns.yaml', 'mistakes.yaml', 'stats.yaml']);
        const newFiles = new Set(Object.keys(manifest.files));
        let removed = 0;
        for (const rel of Object.keys(previousManifest.files)) {
            if (newFiles.has(rel)) continue;
            const base = path.basename(rel);
            if (preserveBases.has(base)) continue;
            const fp = path.join(targetDir, rel);
            if (!fs.existsSync(fp)) continue;
            if (DRY_RUN) { log.dry(`rm stale ${rel}`); continue; }
            try { fs.unlinkSync(fp); removed++; log.verbose(`removed stale ${rel}`); } catch {}
        }
        if (removed > 0) log.ok(`cleaned ${removed} retired file(s)`);
    }

    // Hard-coded sweep of directories the v4 templates no longer contain. Catches
    // stale files left over from older installs whose manifest entries were
    // overwritten without tracking the removal (e.g. slash commands removed
    // between v4.0.x point releases).
    const retiredDirs = ['commands'];
    for (const rel of retiredDirs) {
        const dp = path.join(targetDir, rel);
        const tplDir = path.join(TEMPLATES_DIR, rel);
        if (fs.existsSync(dp) && !fs.existsSync(tplDir)) {
            if (DRY_RUN) { log.dry(`rm -rf ${dp}`); }
            else {
                try {
                    removeDir(dp);
                    fs.rmdirSync(dp);
                    log.ok(`cleaned retired ${rel}/ directory`);
                } catch {}
            }
        }
    }

    // Best-effort: prune now-empty directories tracked in the old manifest.
    if (previousManifest && previousManifest.directories) {
        const oldDirs = previousManifest.directories;
        for (const rel of [...oldDirs].sort((a, b) => b.length - a.length)) {
            const dp = path.join(targetDir, rel);
            if (!fs.existsSync(dp)) continue;
            try {
                if (fs.readdirSync(dp).length === 0) fs.rmdirSync(dp);
            } catch {}
        }
    }

    saveManifest(targetDir, manifest);
    saveVersion(targetDir, CURRENT_VERSION);

    log.head('INSTALL COMPLETE');
    console.log(`Installed v${CURRENT_VERSION} to ${targetDir}`);
    console.log('Restart your Droid CLI to apply hook changes.');
    console.log('');
    console.log('Try it:');
    console.log('  npx droidpartment status');
    console.log('  npx droidpartment doctor');
    console.log(`  ${dptBin} stats`);
    console.log(`  ${dptBin} run -- echo hello`);
    return true;
}

function uninstall(targetDir, purgeMemory) {
    if (!isInstalled(targetDir)) {
        log.head('NOTHING TO UNINSTALL');
        log.info(`Droidpartment is not installed in ${targetDir}`);
        return true;
    }
    log.head('UNINSTALLING DROIDPARTMENT');
    const manifest = loadManifest(targetDir);

    if (manifest && manifest.files) {
        const preserve = new Set(['lessons.yaml', 'patterns.yaml', 'mistakes.yaml', 'stats.yaml']);
        let removed = 0, preserved = 0;
        for (const rel of Object.keys(manifest.files)) {
            const base = path.basename(rel);
            if (preserve.has(base) && !purgeMemory) {
                preserved++;
                log.verbose(`preserved ${rel}`);
                continue;
            }
            const fp = path.join(targetDir, rel);
            if (fs.existsSync(fp)) {
                if (DRY_RUN) { log.dry(`rm ${fp}`); continue; }
                try { fs.unlinkSync(fp); removed++; } catch {}
            }
        }
        log.ok(`removed ${removed} tracked file(s); preserved ${preserved} learning file(s)`);

        const dirs = [...(manifest.directories || [])].sort((a, b) => b.length - a.length);
        for (const rel of dirs) {
            const dp = path.join(targetDir, rel);
            if (!fs.existsSync(dp)) continue;
            try {
                if (fs.readdirSync(dp).length === 0) fs.rmdirSync(dp);
            } catch {}
        }
    } else {
        log.warn('no manifest found; performing best-effort cleanup');
        // best-effort: remove known dirs
        for (const sub of ['droids', 'skills', 'bin', 'plugins']) {
            const dp = path.join(targetDir, sub);
            if (fs.existsSync(dp)) {
                if (DRY_RUN) { log.dry(`rm -rf ${dp}`); continue; }
                removeDir(dp);
                try { fs.rmdirSync(dp); } catch {}
            }
        }
    }

    if (purgeMemory) {
        const memoryDir = path.join(targetDir, 'memory');
        if (fs.existsSync(memoryDir)) {
            if (DRY_RUN) {
                log.dry(`rm -rf ${memoryDir}`);
            } else {
                removeDir(memoryDir);
                try { fs.rmdirSync(memoryDir); } catch {}
                log.ok('purged memory/');
            }
        }
        const rawDir = path.join(targetDir, 'raw-output');
        if (fs.existsSync(rawDir)) {
            if (!DRY_RUN) {
                removeDir(rawDir);
                try { fs.rmdirSync(rawDir); } catch {}
                log.ok('purged raw-output/');
            }
        }
    }

    unregisterHooks(targetDir);

    for (const f of [VERSION_FILE, MANIFEST_FILE, 'AGENTS.md']) {
        const fp = path.join(targetDir, f);
        if (fs.existsSync(fp)) {
            if (DRY_RUN) log.dry(`rm ${fp}`);
            else { try { fs.unlinkSync(fp); } catch {} }
        }
    }

    log.head('UNINSTALL COMPLETE');
    return true;
}

function dirSizeBytes(dir) {
    if (!fs.existsSync(dir)) return 0;
    let total = 0;
    const stack = [dir];
    while (stack.length) {
        const cur = stack.pop();
        for (const e of fs.readdirSync(cur, { withFileTypes: true })) {
            const p = path.join(cur, e.name);
            if (e.isDirectory()) stack.push(p);
            else { try { total += fs.statSync(p).size; } catch {} }
        }
    }
    return total;
}

function fmtBytes(n) {
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    if (n < 1024 * 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} MB`;
    return `${(n / 1024 / 1024 / 1024).toFixed(2)} GB`;
}

function showStatus() {
    log.head('DROIDPARTMENT STATUS');
    const personal = getInstalledVersion(PERSONAL_DIR);
    const project = getInstalledVersion(PROJECT_DIR);

    console.log(`Personal (~/.factory): ${personal ? `v${personal}` : 'not installed'}`);
    console.log(`Project  (./.factory):  ${project ? `v${project}` : 'not installed'}`);
    console.log(`Available:              v${CURRENT_VERSION}`);

    const targetDir = personal ? PERSONAL_DIR : (project ? PROJECT_DIR : null);
    if (targetDir) {
        const dptBin = dptBinaryAt(targetDir);
        const hasBin = fs.existsSync(dptBin);
        console.log(`dpt binary:             ${hasBin ? dptBin : 'MISSING'}`);
        if (hasBin) {
            const r = spawnSync(dptBin, ['--version'], { encoding: 'utf8' });
            if (r.status === 0) console.log(`dpt --version:          ${r.stdout.trim()}`);
        }
        const droidsDir = path.join(targetDir, 'droids');
        if (fs.existsSync(droidsDir)) {
            const n = fs.readdirSync(droidsDir).filter(f => f.endsWith('.md')).length;
            console.log(`sub-droids:             ${n}`);
        }
        const skillsDir = path.join(targetDir, 'skills');
        if (fs.existsSync(skillsDir)) {
            const n = fs.readdirSync(skillsDir, { withFileTypes: true }).filter(d => d.isDirectory()).length;
            console.log(`skills:                 ${n}`);
        }
        const cmdsDir = path.join(targetDir, 'commands');
        if (fs.existsSync(cmdsDir)) {
            const n = fs.readdirSync(cmdsDir).filter(f => f.endsWith('.md')).length;
            console.log(`slash commands:         ${n}`);
        }
        const settingsPath = settingsPathFor(targetDir);
        const { settings, parseError } = readSettingsStrict(settingsPath);
        if (parseError) {
            console.log('hooks registered:       (settings.json could not be parsed)');
        } else {
            const hooks = settings && settings.hooks ? Object.keys(settings.hooks).length : 0;
            console.log(`hooks registered:       ${hooks}`);
            if (settings && settings.hooksDisabled) {
                console.log(`                        (hooksDisabled is true - hooks will not run)`);
            }
        }
        const settingsDir = path.dirname(settingsPath);
        if (fs.existsSync(settingsDir)) {
            const baks = fs.readdirSync(settingsDir).filter(f => f.startsWith('settings.json.') && f.includes('bak'));
            if (baks.length > 0) console.log(`settings.json backups:  ${baks.length}`);
        }
        const rawDir = path.join(targetDir, 'raw-output');
        if (fs.existsSync(rawDir)) {
            const size = dirSizeBytes(rawDir);
            const days = fs.readdirSync(rawDir, { withFileTypes: true }).filter(d => d.isDirectory()).length;
            console.log(`raw-output:             ${days} day(s) on disk, ${fmtBytes(size)}`);
        }
    }
}

function doctor() {
    log.head('DOCTOR');
    let issues = 0;

    const personal = getInstalledVersion(PERSONAL_DIR);
    if (!personal) {
        log.warn('not installed in ~/.factory');
        issues++;
    } else {
        log.ok(`installed v${personal}`);
    }

    const targetDir = personal ? PERSONAL_DIR : null;
    if (targetDir) {
        const dpt = dptBinaryAt(targetDir);
        if (!fs.existsSync(dpt)) {
            log.err(`dpt binary missing at ${dpt}`);
            issues++;
        } else {
            const r = spawnSync(dpt, ['--version'], { encoding: 'utf8' });
            if (r.status !== 0) { log.err('dpt binary not executable'); issues++; }
            else log.ok(`dpt OK: ${r.stdout.trim()}`);
        }

        if (detectV3PythonInstall(targetDir)) {
            log.warn('legacy Python files still present - run `npx droidpartment update`');
            issues++;
        } else {
            log.ok('no legacy Python files');
        }
    }

    const settingsPath = settingsPathFor(targetDir || PERSONAL_DIR);
    if (fs.existsSync(settingsPath)) {
        const { settings, parseError } = readSettingsStrict(settingsPath);
        if (parseError) {
            log.err(`settings.json is not valid JSON: ${parseError.message}`);
            issues++;
        } else if (!settings.hooks || !settings.hooks.SessionStart) {
            log.warn('SessionStart hook missing in settings.json');
            issues++;
        } else {
            log.ok(`hooks registered (${Object.keys(settings.hooks).length} events)`);
        }
    } else {
        log.warn(`no settings.json at ${settingsPath}`);
        issues++;
    }

    if (issues === 0) log.ok('all checks passed');
    else log.warn(`${issues} issue(s) found`);
    return issues === 0 ? EXIT_OK : EXIT_ERROR;
}

function showBanner() {
    if (VERBOSITY < 1) return;
    console.log(`\n${COLORS.bright}${COLORS.cyan}Droidpartment${COLORS.reset} v${CURRENT_VERSION}`);
    console.log(`${COLORS.dim}Token-saving multi-agent orchestration for Factory Droid CLI${COLORS.reset}\n`);
}

function showHelp() {
    console.log(`
Droidpartment v${CURRENT_VERSION}

USAGE:
  npx droidpartment [command] [options]

COMMANDS:
  install      Install Droidpartment to ~/.factory
  update       Update an existing install (migrates v3 Python -> v4 Rust)
  reinstall    Uninstall then install (preserves learning YAMLs unless --purge)
  uninstall    Remove Droidpartment (preserves learning YAMLs unless --purge)
  status       Show install version, binary path, hook wiring, savings
  doctor       Run diagnostics

OPTIONS:
  -q, --quiet      minimal output
  -v, --verbose    detailed output
  --project        install to ./.factory instead of ~/.factory
  --force          force overwrite even if same version
  --dry-run        preview without writing
  --purge          delete YAML memory on uninstall
  --version        print version
  --help           print help

EXAMPLES:
  npx droidpartment install
  npx droidpartment update
  npx droidpartment status
  npx droidpartment uninstall --purge
`);
}

function parseArgs(argv) {
    const flags = {
        quiet: false, verbose: false, project: false,
        force: false, dryRun: false, purge: false, version: false, help: false,
    };
    let command = null;
    const cmds = new Set(['install', 'update', 'uninstall', 'reinstall', 'status', 'doctor']);
    for (const a of argv) {
        if (cmds.has(a)) command = a;
        else if (a === '-q' || a === '--quiet') flags.quiet = true;
        else if (a === '-v' || a === '--verbose') flags.verbose = true;
        else if (a === '--project') flags.project = true;
        else if (a === '--force') flags.force = true;
        else if (a === '--dry-run') flags.dryRun = true;
        else if (a === '--purge') flags.purge = true;
        else if (a === '--version') flags.version = true;
        else if (a === '--help' || a === '-h') flags.help = true;
        else if (a === '-y' || a === '--yes') { /* legacy no-op: install is always non-interactive */ }
        else if (a.startsWith('-')) log.warn(`unknown option: ${a}`);
    }
    return { command, flags };
}

function main() {
    const { command, flags } = parseArgs(process.argv.slice(2));
    if (flags.quiet) VERBOSITY = 0;
    if (flags.verbose) VERBOSITY = 2;
    DRY_RUN = flags.dryRun;

    if (flags.version) {
        console.log(`droidpartment v${CURRENT_VERSION}`);
        process.exit(EXIT_OK);
    }
    if (flags.help) { showHelp(); process.exit(EXIT_OK); }

    showBanner();

    const targetDir = flags.project ? PROJECT_DIR : PERSONAL_DIR;

    if (command === 'status') { showStatus(); process.exit(EXIT_OK); }
    if (command === 'doctor') { process.exit(doctor()); }

    if (command === 'uninstall') {
        const ok = uninstall(targetDir, flags.purge);
        process.exit(ok ? EXIT_OK : EXIT_ERROR);
    }

    if (command === 'reinstall') {
        if (isInstalled(targetDir)) uninstall(targetDir, flags.purge);
        const ok = install(targetDir);
        process.exit(ok ? EXIT_OK : EXIT_ERROR);
    }

    // default / install / update
    const installed = getInstalledVersion(targetDir);
    if (!installed) {
        const ok = install(targetDir);
        process.exit(ok ? EXIT_OK : EXIT_ERROR);
    }

    const cmp = compareVersions(CURRENT_VERSION, installed);
    if (cmp > 0 || flags.force || command === 'update') {
        log.info(`updating ${installed} -> ${CURRENT_VERSION}`);
        const ok = install(targetDir);
        process.exit(ok ? EXIT_OK : EXIT_ERROR);
    } else if (cmp === 0) {
        log.ok(`already up to date (v${installed})`);
        process.exit(EXIT_OK);
    } else {
        log.warn(`installed v${installed} is newer than package v${CURRENT_VERSION}`);
        process.exit(EXIT_OK);
    }
}

main().catch(err => {
    log.err(err.message || String(err));
    if (VERBOSITY >= 2 && err.stack) console.error(err.stack);
    process.exit(EXIT_ERROR);
});
