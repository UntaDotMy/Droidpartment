#!/usr/bin/env node
/**
 * End-to-end installer test suite. Runs against bin/install.js in temp
 * directories. Never touches the user's ~/.factory.
 *
 *   node tests/install.test.js
 *
 * Each test creates a fresh temp dir, optionally seeds it (an existing
 * settings.json, a fake v3 Python layout, etc.), runs the installer, and
 * asserts the resulting state.
 */

'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const REPO = path.resolve(__dirname, '..');
const INSTALL_JS = path.join(REPO, 'bin', 'install.js');
const RUST_BIN = path.join(REPO, 'rust', 'target', 'release', process.platform === 'win32' ? 'dpt.exe' : 'dpt');

const RESET = '\x1b[0m';
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const CYAN = '\x1b[36m';
const DIM = '\x1b[2m';

let pass = 0;
let fail = 0;
const failures = [];

function mkTmp(prefix = 'dpt-test-') {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
    fs.mkdirSync(path.join(dir, '.factory'), { recursive: true });
    return dir;
}

function rm(dir) {
    try { fs.rmSync(dir, { recursive: true, force: true }); } catch {}
}

function seedSettings(dir, obj) {
    fs.writeFileSync(path.join(dir, '.factory', 'settings.json'), JSON.stringify(obj, null, 2), 'utf8');
}

function seedRaw(dir, raw) {
    fs.writeFileSync(path.join(dir, '.factory', 'settings.json'), raw, 'utf8');
}

function readSettings(dir) {
    const p = path.join(dir, '.factory', 'settings.json');
    if (!fs.existsSync(p)) return null;
    return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function runInstall(cwd, args = ['install', '--project', '--yes', '--quiet']) {
    return spawnSync('node', [INSTALL_JS, ...args], { cwd, encoding: 'utf8' });
}

function assert(cond, msg) {
    if (cond) {
        pass++;
        console.log(`  ${GREEN}PASS${RESET} ${msg}`);
    } else {
        fail++;
        failures.push(msg);
        console.log(`  ${RED}FAIL${RESET} ${msg}`);
    }
}

function header(name) {
    console.log(`\n${CYAN}== ${name} ==${RESET}`);
}

function preflight() {
    if (!fs.existsSync(RUST_BIN)) {
        console.error(`${RED}missing Rust binary at ${RUST_BIN}${RESET}`);
        console.error(`${YELLOW}run: cd rust && cargo build --release${RESET}`);
        process.exit(1);
    }
    console.log(`${DIM}using rust binary: ${RUST_BIN}${RESET}`);
    console.log(`${DIM}using installer:   ${INSTALL_JS}${RESET}`);
}

// ---------- TESTS ----------

function test1_freshInstall() {
    header('test 1: fresh install (no settings.json)');
    const dir = mkTmp();
    try {
        const r = runInstall(dir);
        assert(r.status === 0, `install exits 0 (got ${r.status})`);
        const s = readSettings(dir);
        assert(s !== null, 'settings.json was created');
        assert(s && s.hooks, 'settings.hooks exists');
        assert(s && s.hooks && Object.keys(s.hooks).length === 9, `9 hook events registered (got ${s && s.hooks ? Object.keys(s.hooks).length : 'none'})`);
        const baks = fs.readdirSync(path.join(dir, '.factory')).filter(f => f.includes('.bak-'));
        assert(baks.length === 0, 'no backup created when no prior settings existed');
    } finally { rm(dir); }
}

function test2_existingNoHooks() {
    header('test 2: existing settings without hooks');
    const dir = mkTmp();
    try {
        seedSettings(dir, {
            enabledPlugins: { 'core@factory-plugins': true },
            customModels: [{ id: 'custom:m1', baseUrl: 'http://example.com', apiKey: 'k' }],
            sessionDefaultSettings: { reasoningEffort: 'high' },
        });
        const r = runInstall(dir);
        assert(r.status === 0, `install exits 0 (got ${r.status}) -- ${r.stderr || ''}`);
        const s = readSettings(dir);
        assert(s.enabledPlugins && s.enabledPlugins['core@factory-plugins'] === true, 'enabledPlugins preserved');
        assert(s.customModels && s.customModels[0].id === 'custom:m1', 'customModels preserved');
        assert(s.customModels[0].baseUrl === 'http://example.com', 'baseUrl with // preserved');
        assert(s.sessionDefaultSettings && s.sessionDefaultSettings.reasoningEffort === 'high', 'sessionDefaultSettings preserved');
        assert(s.hooks && Object.keys(s.hooks).length === 9, '9 hook events added');
        const baks = fs.readdirSync(path.join(dir, '.factory')).filter(f => f.includes('.bak-'));
        assert(baks.length === 1, `1 backup file created (got ${baks.length})`);
    } finally { rm(dir); }
}

function test3_existingUnrelatedHooks() {
    header('test 3: existing unrelated hooks (must not stomp)');
    const dir = mkTmp();
    try {
        seedSettings(dir, {
            enabledPlugins: { 'core@factory-plugins': true },
            hooks: {
                PreToolUse: [{
                    matcher: 'Execute',
                    hooks: [{ type: 'command', command: 'echo unrelated_kept', timeout: 10 }],
                }],
                Stop: [{
                    matcher: '*',
                    hooks: [{ type: 'command', command: '/usr/local/bin/notify-stop.sh', timeout: 5 }],
                }],
            },
        });
        const r = runInstall(dir);
        assert(r.status === 0, `install exits 0 (got ${r.status})`);
        const s = readSettings(dir);
        assert(s.enabledPlugins['core@factory-plugins'] === true, 'enabledPlugins preserved');
        assert(s.hooks.PreToolUse.length === 2, `PreToolUse: 1 unrelated + 1 dpt = 2 (got ${s.hooks.PreToolUse.length})`);
        assert(s.hooks.PreToolUse[0].hooks[0].command === 'echo unrelated_kept', 'unrelated PreToolUse kept first');
        assert(/dpt(\.exe)?.* hook pre-tool-use/.test(s.hooks.PreToolUse[1].hooks[0].command), 'dpt PreToolUse appended');
        assert(s.hooks.Stop.length === 2, `Stop: 1 unrelated + 1 dpt = 2 (got ${s.hooks.Stop.length})`);
        assert(s.hooks.Stop[0].hooks[0].command === '/usr/local/bin/notify-stop.sh', 'unrelated Stop kept first');
    } finally { rm(dir); }
}

function test4_reinstallReplaces() {
    header('test 4: re-install with --force (existing dpt hooks replaced, not duplicated)');
    const dir = mkTmp();
    try {
        // First install
        let r = runInstall(dir);
        assert(r.status === 0, 'first install exits 0');
        const s1 = readSettings(dir);
        assert(s1.hooks.SessionStart.length === 1, 'after first install: 1 SessionStart');

        // Second install with --force triggers an actual re-write (same version otherwise no-ops).
        r = spawnSync('node', [INSTALL_JS, 'install', '--project', '--yes', '--force', '--quiet'], { cwd: dir, encoding: 'utf8' });
        assert(r.status === 0, `second install (--force) exits 0 (got ${r.status}) -- ${r.stderr || ''}`);
        const s2 = readSettings(dir);
        assert(s2.hooks.SessionStart.length === 1, `after re-install: still 1 SessionStart (got ${s2.hooks.SessionStart.length})`);
        assert(s2.hooks.PreToolUse.length === 1, `after re-install: still 1 PreToolUse (got ${s2.hooks.PreToolUse.length})`);
        const baks = fs.readdirSync(path.join(dir, '.factory')).filter(f => f.includes('.bak-'));
        assert(baks.length >= 1, `at least one backup created on re-install (got ${baks.length})`);
    } finally { rm(dir); }
}

function test5_invalidJsonRefused() {
    header('test 5: invalid JSON refuses to write');
    const dir = mkTmp();
    try {
        const corrupt = '{ "this is { broken JSON\n  customModels: [\n}';
        seedRaw(dir, corrupt);
        const before = fs.readFileSync(path.join(dir, '.factory', 'settings.json'), 'utf8');
        const r = runInstall(dir, ['install', '--project', '--yes']); // not --quiet so we see the message
        assert(r.status === 0, `install exits 0 even when hooks skipped (got ${r.status})`);
        const after = fs.readFileSync(path.join(dir, '.factory', 'settings.json'), 'utf8');
        assert(before === after, 'settings.json untouched when JSON unparseable');
        const baks = fs.readdirSync(path.join(dir, '.factory')).filter(f => f.includes('.bak-'));
        assert(baks.length === 0, `no backup created when refusing to write (got ${baks.length})`);
        assert(/Refusing to modify/.test(r.stderr || r.stdout || ''), 'prints "Refusing to modify"');
    } finally { rm(dir); }
}

function test6_v3PythonMigration() {
    header('test 6: v3 -> v4 migration removes Python files');
    const dir = mkTmp();
    try {
        // Seed a fake v3 install
        const memDir = path.join(dir, '.factory', 'memory');
        const hooksDir = path.join(memDir, 'hooks');
        fs.mkdirSync(hooksDir, { recursive: true });
        for (const f of ['hook-session-start.py', 'hook-user-prompt-submit.py', 'hook-pre-tool-use.py']) {
            fs.writeFileSync(path.join(hooksDir, f), `# legacy ${f}\n`);
        }
        for (const f of ['cache_manager.py', 'context_index.py', 'shared_context.py']) {
            fs.writeFileSync(path.join(memDir, f), `# legacy ${f}\n`);
        }
        // Seed YAML data we want preserved
        fs.writeFileSync(path.join(memDir, 'lessons.yaml'), 'lessons:\n  - id: lesson_1\n    lesson: keep this\n');
        fs.writeFileSync(path.join(memDir, 'mistakes.yaml'), 'mistakes: []\n');
        fs.mkdirSync(path.join(memDir, 'projects', 'sample'), { recursive: true });
        fs.writeFileSync(path.join(memDir, 'projects', 'sample', 'lessons.yaml'), 'lessons: []\n');

        const r = runInstall(dir);
        assert(r.status === 0, 'install exits 0');
        assert(!fs.existsSync(hooksDir), 'memory/hooks/ removed');
        assert(!fs.existsSync(path.join(memDir, 'cache_manager.py')), 'cache_manager.py removed');
        assert(!fs.existsSync(path.join(memDir, 'context_index.py')), 'context_index.py removed');
        assert(!fs.existsSync(path.join(memDir, 'shared_context.py')), 'shared_context.py removed');
        const lessons = fs.readFileSync(path.join(memDir, 'lessons.yaml'), 'utf8');
        assert(lessons.includes('keep this'), 'lessons.yaml preserved (user data)');
        assert(fs.existsSync(path.join(memDir, 'projects', 'sample', 'lessons.yaml')), 'project memory preserved');
        const dptBin = path.join(dir, '.factory', 'bin', process.platform === 'win32' ? 'dpt.exe' : 'dpt');
        assert(fs.existsSync(dptBin), 'rust dpt binary installed');
    } finally { rm(dir); }
}

function test7_uninstallSurgical() {
    header('test 7: uninstall removes only dpt hooks');
    const dir = mkTmp();
    try {
        // Seed an install + extra unrelated hooks
        seedSettings(dir, {
            enabledPlugins: { 'core@factory-plugins': true },
            hooks: {
                Stop: [{ matcher: '*', hooks: [{ type: 'command', command: '/usr/local/bin/notify.sh', timeout: 5 }] }],
            },
        });
        let r = runInstall(dir);
        assert(r.status === 0, 'install exits 0');
        let s = readSettings(dir);
        assert(s.hooks.Stop.length === 2, `after install: 2 Stop handlers (got ${s.hooks.Stop.length})`);

        r = spawnSync('node', [INSTALL_JS, 'uninstall', '--project', '--yes', '--quiet'], { cwd: dir, encoding: 'utf8' });
        assert(r.status === 0, `uninstall exits 0 (got ${r.status}) -- ${r.stderr || ''}`);
        s = readSettings(dir);
        assert(s.enabledPlugins && s.enabledPlugins['core@factory-plugins'] === true, 'enabledPlugins still preserved after uninstall');
        assert(s.hooks && s.hooks.Stop && s.hooks.Stop.length === 1, `Stop has 1 unrelated handler (got ${s.hooks && s.hooks.Stop ? s.hooks.Stop.length : 'none'})`);
        assert(s.hooks.Stop[0].hooks[0].command === '/usr/local/bin/notify.sh', 'unrelated Stop kept');
        assert(!s.hooks.SessionStart, 'dpt SessionStart removed');
        assert(!s.hooks.PreToolUse, 'dpt PreToolUse removed (only dpt was registered there)');
    } finally { rm(dir); }
}

function test8_updateInPlace() {
    header('test 8: update on existing v4 install (no duplication, settings preserved)');
    const dir = mkTmp();
    try {
        seedSettings(dir, {
            customModels: [{ id: 'custom:m', baseUrl: 'https://api.example.com' }],
        });
        let r = runInstall(dir);
        assert(r.status === 0, 'first install exits 0');
        r = spawnSync('node', [INSTALL_JS, 'update', '--project', '--yes', '--quiet'], { cwd: dir, encoding: 'utf8' });
        assert(r.status === 0, `update exits 0 (got ${r.status})`);
        const s = readSettings(dir);
        assert(s.customModels && s.customModels[0].id === 'custom:m', 'customModels still preserved');
        assert(s.hooks && s.hooks.SessionStart && s.hooks.SessionStart.length === 1, 'still 1 SessionStart after update');
    } finally { rm(dir); }
}

function test9_legacyPythonHooksReplaced() {
    header('test 9: legacy v3 python hook entries in settings.json detected and replaced');
    const dir = mkTmp();
    try {
        // Seed settings.json with legacy "python ... hook-*.py" entries (the v3 install pattern).
        seedSettings(dir, {
            enabledPlugins: { 'core@factory-plugins': true },
            hooks: {
                SessionStart: [{
                    matcher: '*',
                    hooks: [{
                        type: 'command',
                        command: 'python C:/Users/test/.factory/memory/hooks/hook-session-start.py',
                        timeout: 30,
                    }],
                }],
                PostToolUse: [{
                    matcher: '*',
                    hooks: [{
                        type: 'command',
                        command: 'python3 ~/.factory/memory/hooks/hook-post-tool-use.py',
                        timeout: 10,
                    }],
                }],
                // unrelated entry that must survive
                Stop: [{
                    matcher: '*',
                    hooks: [{ type: 'command', command: '/usr/local/bin/notify.sh', timeout: 5 }],
                }],
            },
        });
        const r = runInstall(dir);
        assert(r.status === 0, `install exits 0 (got ${r.status}) -- ${r.stderr || ''}`);
        const s = readSettings(dir);
        assert(s.enabledPlugins['core@factory-plugins'] === true, 'enabledPlugins preserved');
        assert(s.hooks.SessionStart.length === 1, `SessionStart should be replaced (got ${s.hooks.SessionStart.length} entries)`);
        const sessCmd = s.hooks.SessionStart[0].hooks[0].command;
        assert(/dpt(\.exe)?\b[^\w]+hook\b/.test(sessCmd), 'SessionStart now points at dpt');
        assert(!/hook-session-start\.py/.test(sessCmd), 'legacy python hook-*.py entry removed');
        const postCmd = s.hooks.PostToolUse[0].hooks[0].command;
        assert(/dpt(\.exe)?\b[^\w]+hook\b/.test(postCmd), 'PostToolUse now points at dpt');
        assert(s.hooks.Stop.length === 2, `Stop has unrelated + dpt = 2 entries (got ${s.hooks.Stop.length})`);
        assert(s.hooks.Stop[0].hooks[0].command === '/usr/local/bin/notify.sh', 'unrelated Stop entry kept');
    } finally { rm(dir); }
}

function test10_hookCommandFormat() {
    header('test 10: hook command format (no outer quotes when path has no spaces)');
    const dir = mkTmp();
    try {
        const r = runInstall(dir);
        assert(r.status === 0, 'install exits 0');
        const s = readSettings(dir);
        const cmd = s.hooks.SessionStart[0].hooks[0].command;
        // Path under %TEMP% never has spaces, so the command must NOT have outer quotes.
        assert(!cmd.startsWith('"'), `command should not start with quote (got: ${cmd})`);
        assert(/dpt(\.exe)?\s+hook\s+session-start/.test(cmd), `command shape OK (got: ${cmd})`);
    } finally { rm(dir); }
}

function test11_urlInSettingsParsesCleanly() {
    header('test 11: URLs with // in settings do not confuse the JSONC stripper');
    const dir = mkTmp();
    try {
        seedSettings(dir, {
            customModels: [
                { id: 'custom:m1', baseUrl: 'http://45.77.34.141:8080/v1', apiKey: 'k' },
                { id: 'custom:m2', baseUrl: 'https://api.example.com/v2/path' },
            ],
            hooks: { /* no prior hooks */ },
        });
        const r = runInstall(dir);
        assert(r.status === 0, `install exits 0 (got ${r.status}) -- ${r.stderr || ''}`);
        const s = readSettings(dir);
        assert(s.customModels.length === 2, 'both customModels preserved');
        assert(s.customModels[0].baseUrl === 'http://45.77.34.141:8080/v1', 'http:// URL preserved');
        assert(s.customModels[1].baseUrl === 'https://api.example.com/v2/path', 'https:// URL preserved');
        assert(s.hooks && Object.keys(s.hooks).length === 9, '9 hook events added');
    } finally { rm(dir); }
}

function test12_noManualSlashCommands() {
    header('test 12: no manual /dpt-* slash commands shipped (everything must be automated)');
    const dir = mkTmp();
    try {
        const r = runInstall(dir);
        assert(r.status === 0, 'install exits 0');
        const cmdsDir = path.join(dir, '.factory', 'commands');
        if (fs.existsSync(cmdsDir)) {
            const cmds = fs.readdirSync(cmdsDir).filter(f => f.endsWith('.md'));
            assert(cmds.length === 0, `no slash commands installed (got ${cmds.length}: ${cmds.join(', ')})`);
        } else {
            assert(true, 'no commands directory (expected for automated-only flows)');
        }
    } finally { rm(dir); }
}

function test13_hooksDisabledRespected() {
    header('test 13: hooksDisabled=true means hooks are NOT registered');
    const dir = mkTmp();
    try {
        seedSettings(dir, {
            enabledPlugins: { 'core@factory-plugins': true },
            hooksDisabled: true,
        });
        const r = runInstall(dir, ['install', '--project', '--yes']);
        assert(r.status === 0, `install exits 0 (got ${r.status})`);
        const s = readSettings(dir);
        assert(s.enabledPlugins['core@factory-plugins'] === true, 'enabledPlugins preserved');
        assert(s.hooksDisabled === true, 'hooksDisabled preserved');
        assert(!s.hooks || Object.keys(s.hooks).length === 0, 'no hooks added when disabled');
        assert(/hooksDisabled is true/.test(r.stdout || ''), 'prints hooksDisabled message');
    } finally { rm(dir); }
}

function test14_settingsLocalJsonOverlay() {
    header('test 14: settings.local.json overlay can disable hooks');
    const dir = mkTmp();
    try {
        seedSettings(dir, { enabledPlugins: { 'core@factory-plugins': true } });
        // settings.local.json overrides settings.json by setting hooksDisabled
        fs.writeFileSync(
            path.join(dir, '.factory', 'settings.local.json'),
            JSON.stringify({ hooksDisabled: true }, null, 2),
            'utf8'
        );
        const r = runInstall(dir, ['install', '--project', '--yes']);
        assert(r.status === 0, `install exits 0 (got ${r.status})`);
        const s = readSettings(dir);
        assert(s.enabledPlugins['core@factory-plugins'] === true, 'enabledPlugins preserved');
        assert(!s.hooks || Object.keys(s.hooks).length === 0, 'no hooks added when local override disables them');
    } finally { rm(dir); }
}

function test15_backupRetention() {
    header('test 15: backup retention keeps only N most recent');
    const dir = mkTmp();
    try {
        seedSettings(dir, { enabledPlugins: { 'core@factory-plugins': true } });
        for (let i = 0; i < 5; i++) {
            const r = spawnSync('node', [INSTALL_JS, 'install', '--project', '--yes', '--force', '--quiet'], { cwd: dir, encoding: 'utf8' });
            assert(r.status === 0, `install ${i + 1} exits 0`);
            const wait = Date.now() + 25;
            while (Date.now() < wait) {}
        }
        const baks = fs.readdirSync(path.join(dir, '.factory')).filter(f => f.includes('.bak-'));
        assert(baks.length <= 3, `backup retention kept <= 3 files (got ${baks.length})`);
    } finally { rm(dir); }
}

function test16_deltaPatchCleansRetiredFiles() {
    header('test 16: delta-patch removes files dropped from new template');
    const dir = mkTmp();
    try {
        // First install brings in current templates
        let r = runInstall(dir);
        assert(r.status === 0, 'first install exits 0');

        // Inject a "retired" file into the manifest by hand: simulate a previous
        // template version that shipped /commands/old-command.md
        const cmdsDir = path.join(dir, '.factory', 'commands');
        fs.mkdirSync(cmdsDir, { recursive: true });
        const retired = path.join(cmdsDir, 'old-command.md');
        fs.writeFileSync(retired, '---\nname: old-command\n---\nlegacy', 'utf8');
        const manifestPath = path.join(dir, '.factory', '.droidpartment-manifest.json');
        const m = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
        m.files['commands/old-command.md'] = { size: 35, type: 'md' };
        if (!m.directories.includes('commands')) m.directories.push('commands');
        fs.writeFileSync(manifestPath, JSON.stringify(m, null, 2), 'utf8');

        // Re-install with --force should detect the retired file is no longer in
        // the new manifest and delete it.
        r = spawnSync('node', [INSTALL_JS, 'install', '--project', '--yes', '--force', '--quiet'], { cwd: dir, encoding: 'utf8' });
        assert(r.status === 0, `re-install exits 0 (got ${r.status})`);
        assert(!fs.existsSync(retired), 'retired old-command.md was cleaned up');
    } finally { rm(dir); }
}

// ---------- DRIVER ----------

function main() {
    preflight();
    test1_freshInstall();
    test2_existingNoHooks();
    test3_existingUnrelatedHooks();
    test4_reinstallReplaces();
    test5_invalidJsonRefused();
    test6_v3PythonMigration();
    test7_uninstallSurgical();
    test8_updateInPlace();
    test9_legacyPythonHooksReplaced();
    test10_hookCommandFormat();
    test11_urlInSettingsParsesCleanly();
    test12_noManualSlashCommands();
    test13_hooksDisabledRespected();
    test14_settingsLocalJsonOverlay();
    test15_backupRetention();
    test16_deltaPatchCleansRetiredFiles();

    console.log(`\n${CYAN}== summary ==${RESET}`);
    console.log(`${GREEN}${pass} passed${RESET}, ${fail > 0 ? RED : GREEN}${fail} failed${RESET}`);
    if (failures.length) {
        console.log(`\n${RED}failures:${RESET}`);
        for (const f of failures) console.log(`  - ${f}`);
    }
    process.exit(fail === 0 ? 0 : 1);
}

main();
